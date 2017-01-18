"""Modul to handle requests."""
import logging
import urllib
import urlparse
import transaction
from pyramid.httpexceptions import HTTPFound
from formbar.form import Validator
from ringo.lib.security import (
    has_permission,
    ValueChecker
)
from ringo.lib.helpers import import_model, get_action_routename, literal
from ringo.lib.history import History
from ringo.lib.sql.cache import invalidate_cache
from ringo.views.helpers import (
    get_item_from_request,
    get_ownership_form,
    get_item_form,
    get_item_modul,
    get_current_form_page,
    set_current_form_page,
    get_next_form_page
)

log = logging.getLogger(__name__)


def form_has_errors(field, data, context):
    """Simple validation callback which returns True if the form has not
    errors an validation. Please make sure that this validators gets
    called as last validator of all validators get the final result of
    the validation."""
    # context is the current formbar form.
    return not context.has_errors()


def encode_unicode_dict(unicodedict, encoding="utf-8"):
    bytedict = {}
    for key in unicodedict:
        if isinstance(unicodedict[key], unicode):
            bytedict[key] = unicodedict[key].encode(encoding)
        elif isinstance(unicodedict[key], dict):
            bytedict[key] = encode_unicode_dict(unicodedict[key])
        else:
            bytedict[key] = unicodedict[key]
    return bytedict


def decode_bytestring_dict(bytedict, encoding="utf-8"):
    unicodedict = {}
    for key in bytedict:
        if isinstance(bytedict[key], str):
            unicodedict[key] = bytedict[key].decode(encoding)
        elif isinstance(bytedict[key], dict):
            unicodedict[key] = decode_bytestring_dict(bytedict[key])
        else:
            unicodedict[key] = bytedict[key]
    return unicodedict


def encode_values(values):
    """Returns a string with encode the values in the given dictionary.

    :values: dictionary with key values pairs
    :returns: String key1:value1,key2:value2...

    """
    # Because urlencode can not handle unicode strings we encode the
    # whole dictionary into utf8 bytestrings first.
    return urllib.urlencode(encode_unicode_dict(values))


def decode_values(encoded):
    """Returns a dictionay with decoded values in the string. See
    encode_values function.

    :encoded : String key1:value1,key2:value2...
    :returns: Dictionary with key values pairs
    """
    # We convert the encoded querystring into a bystring to enforce that
    # parse_pq returns a dictionary which can be later decoded using
    # decode_bystring_dict. If we use the encoded string directly the
    # returned dicionary would contain bytestring as unicode. e.g
    # u'M\xc3\xbcller' which can't be decoded later.
    encoded = str(encoded)

    # Now convert the query string into a dictionary with UTF-8 encoded
    # bytestring values.
    values = urlparse.parse_qs(encoded)
    for key in values:
        values[key] = values[key][0]
    # Finally convert this dictionary back into a unicode dictionary
    return decode_bytestring_dict(values)


def is_confirmed(request):
    """Returns True id the request is confirmed"""
    return request.params.get('confirmed') == "1"


def handle_event(request, item, event):
    """Will call the event listeners for the given event on every base
    class of the given item."""
    for class_ in item.__class__.__bases__:
        if hasattr(class_, event + '_handler'):
            handler = getattr(class_, event + '_handler')
            handler(request, item)


def handle_callback(request, callback, item=None):
    """Will call the given callback

    :request: Current request
    :callback: Callable function or list of callable functions
    :item: item for which the callback will be called.
    :returns: item

    """
    if not item:
        item = get_item_from_request(request)
    if isinstance(callback, list):
        for cb in callback:
            item = cb(request, item)
    elif callback:
        item = callback(request, item)
    return item


def get_relation_item(request):
    clazz = request.context.__model__
    addrelation = request.session.get('%s.addrelation' % clazz)
    if not addrelation:
        addrelation = request.params.get("addrelation")
        if not addrelation:
            return None
    rrel, rclazz, rid = addrelation.split(':')
    parent = import_model(rclazz)
    factory = parent.get_item_factory()
    item = factory.load(rid, db=request.db)
    return item, rrel



def handle_add_relation(request, item):
    """Handle linking of the new item to antoher relation. The relation
    was provided as GET parameter in the current request and is now
    saved in the session.

    :request: Current request
    :item: new item with should be linked

    """
    relation_tuple = get_relation_item(request)
    if relation_tuple:
        rrel = relation_tuple[1]
        pitem = relation_tuple[0]
        clazz = request.context.__model__
        log.debug('Linking %s to %s in %s' % (item, pitem, rrel))
        tmpattr = getattr(pitem, rrel)
        tmpattr.append(item)
        # Delete value from session after the relation has been added
        del request.session['%s.addrelation' % clazz]
    else:
        return item
    request.session.save()


def handle_caching(request):
    """Will handle invalidation of the cache

    :request: TODO

    """
    # Invalidate cache
    invalidate_cache()
    clazz = request.context.__model__
    if request.session.get('%s.form' % clazz):
        del request.session['%s.form' % clazz]
    request.session.save()


def handle_POST_request(form, request, callback, event="", renderers=None):
    """@todo: Docstring for handle_POST_request.

    :name: @todo
    :request: @todo
    :callback: @todo
    :renderers: @todo
    :event: Name of the event (update, create...) Used for the event handler
    :returns: True or False

    """
    _ = request.translate
    clazz = request.context.__model__
    item_label = get_item_modul(request, clazz).get_label()
    item = get_item_from_request(request)
    mapping = {'item_type': item_label, 'item': item}

    # Add a *special* validator to the form to trigger rendering a
    # permanent info pane at the top of the form in case of errors on
    # validation. This info has been added because users reported data
    # loss because of formbar/ringo default behaviour of not saving
    # anything in case of errors. Users seems to expect that the valid
    # part of the data has been saved. This info should make the user
    # aware of the fact that nothing has been saved in case of errors.
    error_message = _("The information contained errors. "
                      "<strong>All entries (including error-free) were not "
                      "saved!</strong> Please correct your entries in the "
                      "fields marked in red and resave.")
    form.add_validator(Validator(None, literal(error_message),
                                 callback=form_has_errors,
                                 context=form))

    # Begin a nested transaction. In case an error occours while saving
    # the data the nested transaction will be rolled back. The parent
    # session will be still ok.
    request.db.begin_nested()
    if form.validate(request.params) and "blobforms" not in request.params:
        checker = ValueChecker()
        try:
            if event == "create":
                try:
                    factory = clazz.get_item_factory(request)
                except TypeError:
                    # Old version of get_item_factory method which does
                    # not take an request parameter.
                    factory = clazz.get_item_factory()
                    factory._request = request

                checker.check(clazz, form.data, request)
                item = factory.create(request.user, form.data)
                item.save({}, request)
                request.context.item = item
                handle_add_relation(request, item)
            else:
                values = checker.check(clazz, form.data, request, item)
                item.save(values, request)
            handle_event(request, item, event)
            handle_callback(request, callback)
            handle_caching(request)

            if event == "create":
                msg = _('Created new ${item_type} successfully.',
                        mapping=mapping)
                log_msg = u'User {user.login} created {item_label} {item.id}'\
                    .format(item_label=item_label, item=item, user=request.user)
            else:
                msg = _('Edited ${item_type} "${item}" successfully.',
                        mapping=mapping)
                log_msg = u'User {user.login} edited {item_label} {item.id}'\
                    .format(item_label=item_label, item=item, user=request.user)
            log.info(log_msg)
            request.session.flash(msg, 'success')

            # Set next form page.
            if request.params.get("_submit") == "nextpage":
                table = clazz.__table__
                itemid = item.id
                page = get_next_form_page(form,
                                          get_current_form_page(clazz,
                                                                request))
                set_current_form_page(table, itemid, page, request)

            # In case all is ok merge the nested session.
            request.db.merge(item)
            return True
        except Exception as error:
            request.db.rollback()
            mapping['error'] = unicode(error.message)
            if event == "create":
                log_msg = _(u'User {user.login} created'
                            '{item_label}').format(item_label=item_label,
                                                   user=request.user)
                msg = _('Error while saving new '
                        '${item_type}: ${error}.', mapping=mapping)
            else:
                log_msg = _(u'User {user.login} edited '
                            '{item_label} {item.id}').format(item_label=item_label,
                                                             item=item, user=request.user)
                msg = _('Error while saving '
                        '${item_type} "${item}": ${error}.', mapping=mapping)
            log.exception(log_msg)
            request.session.flash(msg, 'critical')
            return False
    elif "blobforms" in request.params:
        pass
    else:
        request.db.rollback()
        if event == "create":
            msg = _('Error on validation new '
                    '${item_type}.', mapping=mapping)
        else:
            msg = _('Error on validation '
                    '${item_type} "${item}".', mapping=mapping)
        log.debug(msg)
        request.session.flash(msg, 'error')
    return False


def handle_redirect_on_success(request, backurl=None):
    """Will return a redirect. If there has been a saved "backurl" the
    redirect will on on this url. In all other cases the function will
    try to determine if the item in the request can be opened in edit
    mode or not. If the current user is allowed to open the item in
    edit mode then the update view is called. Else the read view is
    called.

    :request: Current request
    :backurl: Optional. Set backurl manually. This will overwrite
    backurls saved in the session. 
    :returns: Redirect
    """

    item = get_item_from_request(request)
    clazz = request.context.__model__
    backurl = backurl or request.session.get('%s.backurl' % clazz)
    if backurl:
        # Redirect to the configured backurl.
        if request.session.get('%s.backurl' % clazz):
            del request.session['%s.backurl' % clazz]
            request.session.save()
        return HTTPFound(location=backurl)
    else:
        # Handle redirect after success.
        # Check if the user is allowed to call the url after saving
        if has_permission("update", item, request):
            route_name = get_action_routename(item, 'update')
            url = request.route_path(route_name, id=item.id)
        else:
            route_name = get_action_routename(item, 'read')
            url = request.route_path(route_name, id=item.id)
        return HTTPFound(location=url)


def handle_history(request):
    history = request.session.get('history')
    if history is None:
        history = History([])
    history.push(request.url)
    request.session['history'] = history


def handle_params(request):
    """Handles varios sytem GET params comming with the request
    Known params are:

     * backurl: A url which should be called instead of the default
       action after the next request succeeds. The backurl will be saved
       in the session and stays there until it is deleted on a
       successfull request. So take care to delete it to not mess up
       with the application logic.
     * form: The name of a alternative form configuration which is
       used for the request.
     * values: A comma separated list of key/value pair. Key and value
       are separated with an ":"
     * addrelation: A ":" separated string 'relation:class:id' to identify that
       a item with id should be linked to the relation of this item.
    """
    clazz = request.context.__model__
    params = {}
    backurl = request.GET.get('backurl')
    if backurl:
        request.session['%s.backurl' % clazz] = backurl
        params['backurl'] = backurl
    values = request.GET.get('values')
    if values:
        params['values'] = {}
        values = decode_values(values)
        for key in values:
            params['values'][key] = values[key]
    form = request.GET.get('form')
    if form:
        #request.session['%s.form' % clazz] = form
        params['form'] = form
    relation = request.GET.get('addrelation')
    if relation:
        request.session['%s.addrelation' % clazz] = relation
        params['addrelation'] = relation
    request.session.save()
    return params


def get_return_value(request):
    """Will return a dictionary of values used as context in the
    templates. The dictionary will include:

    * clazz: clazz of the current request
    * item: item of the current request

    :request: Current request
    :returns: Dictionary with values as context
    """
    rvalues = {}
    clazz = request.context.__model__
    item = get_item_from_request(request)
    rvalues['clazz'] = clazz
    rvalues['item'] = item
    return rvalues
