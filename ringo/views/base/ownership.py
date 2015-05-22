import logging
from ringo.views.helpers import (
    get_ownership_form,
    get_rendered_ownership_form
)
from ringo.views.request import (
    handle_params,
    handle_history,
    get_return_value,
    handle_POST_request,
    handle_redirect_on_success
)

log = logging.getLogger(__name__)


def ownership(request, callback=None, renderers=None):
    """Base method to handle requests to change the ownership.

    :request: Current request
    :callback: Current function which is called after the item has been read.
    :returns: Dictionary.
    """
    handle_history(request)
    handle_params(request)
    form = get_ownership_form(request)
    if request.POST:
         if handle_POST_request(form, request, callback, 'update', renderers):
             return handle_redirect_on_success(request)
    rvalues = get_return_value(request)
    values = {'_roles': [str(r.name) for r in request.user.roles]}
    rvalues['form'] = get_rendered_ownership_form(request)
    return rvalues
