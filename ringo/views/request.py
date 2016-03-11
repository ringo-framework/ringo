"""Modul to handle requests."""
import logging
from pyramid.httpexceptions import HTTPFound
from formbar.form import Validator
from ringo.lib.security import (
    has_permission,
    ValueChecker
)
from ringo.lib.helpers import import_model, get_action_routename, literal
from ringo.lib.sql.cache import invalidate_cache
from ringo.views.helpers import (
    get_item_from_request,
    get_item_modul
)
from ringo.lib.request.helpers import (
    encode_unicode_dict as _encode_unicode_dict,
    decode_bytestring_dict as _decode_bytestring_dict,
    encode_values as _encode_values,
    decode_values as _decode_values
)

log = logging.getLogger(__name__)


def form_has_errors(field, data, context):
    """Simple validation callback which returns True if the form has not
    errors an validation. Please make sure that this validators gets
    called as last validator of all validators get the final result of
    the validation."""
    # context is the current formbar form.
    return not context.has_errors()


# TODO: Mark use of this method as deprecated. Use the inner method
# directlydirectly  (ti) <2016-03-11 09:19>
def encode_unicode_dict(unicodedict, encoding="utf-8"):
    return _encode_unicode_dict(unicodedict, encoding)


# TODO: Mark use of this method as deprecated. Use the inner method
# directlydirectly  (ti) <2016-03-11 09:19>
def decode_bytestring_dict(bytedict, encoding="utf-8"):
    return _decode_bytestring_dict(bytedict, encoding)


# TODO: Mark use of this method as deprecated. Use the inner method
# directlydirectly  (ti) <2016-03-11 09:19>
def encode_values(values):
    return _encode_values(values)


# TODO: Mark use of this method as deprecated. Use the inner method
# directlydirectly  (ti) <2016-03-11 09:19>
def decode_values(encoded):
    return _decode_values(encoded)


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


def handle_add_relation(request, item):
    """Handle linking of the new item to antoher relation. The relation
    was provided as GET parameter in the current request and is now
    saved in the session.

    :request: Current request
    :item: new item with should be linked

    """
    clazz = request.context.__model__
    addrelation = request.session.get('%s.addrelation' % clazz)
    if not addrelation:
        return item
    rrel, rclazz, rid = addrelation.split(':')
    parent = import_model(rclazz)
    pfactory = parent.get_item_factory()
    pitem = pfactory.load(rid)
    log.debug('Linking %s to %s in %s' % (item, pitem, rrel))
    tmpattr = getattr(pitem, rrel)
    tmpattr.append(item)
    # Delete value from session after the relation has been added
    del request.session['%s.addrelation' % clazz]
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


def handle_POST_request(form, request, callback, event, renderers=None):
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
            else:
                values = checker.check(clazz, form.data, request, item)
                item.save(values, request)
            handle_event(request, item, event)
            handle_add_relation(request, item)
            handle_callback(request, callback)
            handle_caching(request)

            if event == "create":
                msg = _('Created new ${item_type} successfully.',
                        mapping=mapping)
                log_msg = u'User {user.login} created {item_label} {item.id}'\
                    .format(item_label=item_label,
                            item=item, user=request.user)
            else:
                msg = _('Edited ${item_type} "${item}" successfully.',
                        mapping=mapping)
                log_msg = u'User {user.login} edited {item_label} {item.id}'\
                    .format(item_label=item_label,
                            item=item, user=request.user)
            log.info(log_msg)
            request.session.flash(msg, 'success')

            return True
        except Exception as error:
            mapping['error'] = unicode(error.message)
            if event == "create":
                msg = _('Error while saving new '
                        '${item_type}: ${error}.', mapping=mapping)
            else:
                msg = _('Error while saving '
                        '${item_type} "${item}": ${error}.', mapping=mapping)
            log.exception(msg)
            request.session.flash(msg, 'error')
    elif "blobforms" in request.params:
        pass
    else:
        if event == "create":
            msg = _('Error on validation new '
                    '${item_type}.', mapping=mapping)
        else:
            msg = _('Error on validation '
                    '${item_type} "${item}".', mapping=mapping)
        log.debug(msg)
        request.session.flash(msg, 'error')
    return False


def handle_redirect_on_success(request):
    """Will return a redirect. If there has been a saved "backurl" the
    redirect will on on this url. In all other cases the function will
    try to determine if the item in the request can be opened in edit
    mode or not. If the current user is allowed to open the item in
    edit mode then the update view is called. Else the read view is
    called.

    :request: Current request
    :returns: Redirect
    """

    item = get_item_from_request(request)
    clazz = request.context.__model__
    backurl = request.session.get('%s.backurl' % clazz)
    if backurl:
        # Redirect to the configured backurl.
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


def handle_params(request):
    """This method is outdated. DO NOT USE this method it will be
    removed. All param handling is done in request.ringo.params now."""
    return {"backurl": request.ringo.params.backurl,
            "values": request.ringo.params.values,
            "form": request.ringo.params.form,
            "addrelation": request.ringo.params.addrelation}


def handle_history(request):
    """This method is outdated. DO NOT USE this method it will be
    removed. All param handling is done in request.ringo.app now."""
    pass


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
