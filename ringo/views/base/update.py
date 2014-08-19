import logging
from ringo.views.response import JSONResponse
from ringo.views.helpers import (
    get_item_form,
    get_rendered_ownership_form,
    get_rendered_logbook_form,
    get_rendered_item_form
)
from ringo.views.request import (
    handle_params,
    handle_history,
    handle_POST_request,
    get_item_from_request,
    get_return_value
)

log = logging.getLogger(__name__)


def update(request, callback=None, renderers={}):
    """Base method to handle update requests. Returns a dictionary of
    values used available in the rendererd template The template to
    render is defined in the view configuration.

    :request: Current request
    :callback: Current function which is called after the item has been read.
    :returns: Dictionary.
    """
    handle_history(request)
    handle_params(request)
    if request.POST:
        # Will trigger a redirec in case of a successfull validation
        redirect = handle_POST_request('update', request, callback, renderers)
        if redirect:
            return redirect
    rvalues = get_return_value(request)
    rvalues['owner'] = get_rendered_ownership_form(request)
    rvalues['logbook'] = get_rendered_logbook_form(request, readonly=True)
    values = {'_roles': [str(r.name) for r in request.user.get_roles()]}
    rvalues['form'] = get_rendered_item_form('update', request,
                                             values, renderers)
    return rvalues


def rest_update(request, callback=None):
    """Updates an item of type clazz. The item is loaded based on the
    unique id value provided in the matchtict object in the current
    request. The item will be updated with the data submitted in the
    current PUT request. Before updating the item the data will be
    validated against the "update" form of the item. If the validation
    fails the item will not be updated. In all cases the item is return as
    JSON object with the item and updated values back to the client. The
    JSON Response will include further details on the reason why the
    validation failed.

    :request: Current request
    :returns: JSON object.
    """
    item = get_item_from_request(request)
    form = get_item_form('update', request)
    if form.validate(request.params):
        item.save(form.data, request)
        return JSONResponse(True, item)
    else:
        # Validation fails! return item
        return JSONResponse(False, item)
