"""Modul to handle requests."""
from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPFound
)
from ringo.lib.security import has_permission
from ringo.lib.history import History


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
        request.context.item = item
    return item

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
            route_name = item.get_action_routename('update')
            url = request.route_path(route_name, id=item.id)
        else:
            route_name = item.get_action_routename('read')
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


def get_current_form_page(clazz, request):
    """Returns the id of the currently selected page. The currently
    selected page is saved in the session. If there is no saved value
    then the the first page is returned

    :clazz: The clazz for which the form is displayed
    :request: Current request
    :returns: id of the currently selected page. Default: 1
    """
    itemid = request.matchdict.get('id')
    item = clazz.__tablename__
    page = request.session.get('%s.%s.form.page' % (item, itemid))
    if page:
        return int(page)
    else:
        return 1


def get_item_from_request(request):
    """On every request pyramid will use a resource factory to load the
    requested resource for the current request. This resource is the
    context for the current request. This function will extract the
    loaded resource from the context. If the context is None, the item
    could not be loaded. In this case raise a 400 HTTP Status code
    exception.

    :request: Current request having the item loaded in the current context
    :returns: Loaded item

    """
    item = request.context.item
    if not item:
        raise HTTPBadRequest()
    return item
