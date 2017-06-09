import logging
from ringo.views.helpers import (
    get_item_form,
    render_item_form
)
from ringo.views.response import JSONResponse
from ringo.views.request import (
    handle_params,
    handle_history,
    handle_callback,
    get_item_from_request,
    get_return_value
)

log = logging.getLogger(__name__)


def read(request, callback=None, renderers=None):
    """Base method to handle read requests. Returns a dictionary of
    values used available in the rendererd template The template to
    render is defined in the view configuration.

    :request: Current request
    :callback: Current function which is called after the item has been read.
    :returns: Dictionary.
    """
    handle_history(request)
    handle_params(request)
    handle_callback(request, callback, mode="pre,default")
    rvalues = get_return_value(request)
    values = {'_roles': [str(r.name) for r in request.user.roles]}
    form = get_item_form('read', request, renderers, values=values)
    rvalues['form'] = render_item_form(request, form)
    handle_callback(request, callback, mode="post")
    return rvalues


def rest_read(request, callback=None):
    """Base method to handle read requests on the REST interface.
    Returns a JSON object of a specific item.

    :request: Current request
    :callback: Current function which is called after the item has been read.
    :returns: JSON object.
    """
    handle_callback(request, callback, mode="pre,default")
    return JSONResponse(True, get_item_from_request(request))
