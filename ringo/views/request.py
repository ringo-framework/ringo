"""Modul to handle requests."""
import logging
from pyramid.httpexceptions import HTTPFound
from ringo.lib.security import has_permission
from ringo.lib.helpers import import_model, get_action_routename
from ringo.lib.history import History
from ringo.lib.sql.cache import invalidate_cache
from ringo.views.helpers import (
    get_item_from_request,
    get_ownership_form,
    get_item_form,
    get_item_modul
)

log = logging.getLogger(__name__)


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
    :callback: Callable function
    :item: item for which the callback will be called.
    :returns: item

    """
    if not item:
        item = get_item_from_request(request)
    if callback:
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

    if form.validate(request.params) and "blobforms" not in request.params:
        try:
            if event == "create":
                factory = clazz.get_item_factory()
                item = factory.create(request.user, form.data)
                mapping['item'] = item
                item.save({}, request)
                request.context.item = item
            else:
                item.save(form.data, request)
            handle_event(request, item, form._config.id)
            handle_callback(request, callback)
            handle_add_relation(request, item)
            handle_caching(request)

            msg = _('Edited ${item_type} "${item}" successfull.',
                    mapping=mapping)
            log.info(msg)
            request.session.flash(msg, 'success')

            return True
        except Exception as error:
            mapping['error'] = unicode(error.message)
            msg = _('Error while saving '
                    '${item_type} "${item}": ${error}.', mapping=mapping)
            log.exception(msg)
            request.session.flash(msg, 'error')
    elif "blobforms" in request.params:
        pass
    else:
        msg = _('Error on validation the data for '
                '${item_type} "${item}".', mapping=mapping)
        log.info(msg)
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
        for kvpair in values.split(','):
            key, value = kvpair.split(':')
            params['values'][key] = value
    form = request.GET.get('form')
    if form:
        request.session['%s.form' % clazz] = form
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
