import logging
from ringo.views.response import JSONResponse
from ringo.views.helpers import (
    get_item_form,
    render_item_form
)
from ringo.views.request import (
    handle_params,
    handle_history,
    handle_POST_request,
    handle_redirect_on_success,
    get_item_from_request,
    get_return_value
)

log = logging.getLogger(__name__)


def update(request, callback=None, renderers=None,
           validators=None, values=None):
    """Base method to handle update requests. This view will render a
    update form to update items on (GET) requests.

    It the user submits the data (POST) that the data will be validated.
    If validation is successfull the item will be saved in the datebase
    and the callback method will be called. Finally a redirect to either
    the backurl or the edit or read mode of the item will be triggered.

    If the validation fails, the form will be rendered again.
    :request: Current request
    :callback: Current function which is called after the item has been read.
    :renderers: Dictionary of external renderers which should be used
                for renderering some form elements.
    :validators: List of external formbar validators which should be
                 added to the form for validation
    :values: Dictionary of additional values which will be available in
             the form
    :returns: Dictionary or Redirect.
    """
    handle_history(request)
    handle_params(request)
    if values is None:
        values = {}
    values['_roles'] = [str(r.name) for r in request.user.roles]
    form = get_item_form('update', request, renderers, validators, values)
    if request.POST:
        if handle_POST_request(form, request, callback, 'update', renderers):
            return handle_redirect_on_success(request)

    rvalues = get_return_value(request)
    rvalues['form'] = render_item_form(request, form)
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
