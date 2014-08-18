import logging
from formbar.form import Form
from ringo.model.mixins import Owned, Logged, Versioned
from ringo.lib.renderer import (
    add_renderers
)
from ringo.views.helpers import (
    get_ownership_form,
    get_logbook_form
)
from ringo.views.response import JSONResponse
from ringo.views.request import (
    handle_params,
    handle_history,
    get_item_from_request,
    get_current_form_page
)

log = logging.getLogger(__name__)


def read(request, callback=None, renderers={}):
    clazz = request.context.__model__
    item = get_item_from_request(request)
    handle_history(request)
    handle_params(clazz, request)
    _ = request.translate
    rvalue = {}

    # Add ringo specific renderers
    renderers = add_renderers(renderers)

    owner_form = get_ownership_form(item, request, readonly=True)
    logbook_form = get_logbook_form(item, request, readonly=True,
                                    renderers=renderers)
    item_form = Form(item.get_form_config('read'), item, request.db,
                     translate=_,
                     renderers=renderers,
                     change_page_callback={'url': 'set_current_form_page',
                                           'item': clazz.__tablename__,
                                           'itemid': item.id},
                     request=request,
                     csrf_token=request.session.get_csrf_token(),
                     eval_url='/rest/rule/evaluate')

    # Validate the form to generate the warnings if the form has not
    # been alreaded validated.
    if not item_form.validated:
        item_form.validate(None)

    if callback:
        item = callback(request, item)

    rvalue['clazz'] = clazz
    rvalue['item'] = item
    if isinstance(item, Owned):
        rvalue['owner'] = owner_form.render()
    else:
        rvalue['owner'] = ""
    if isinstance(item, Logged):
        rvalue['logbook'] = logbook_form.render()
    else:
        rvalue['logbook'] = ""

    if isinstance(item, Versioned):
        previous_values = item.get_previous_values(author=request.user.login)
    else:
        previous_values = {}
    # Add ringo specific values into the renderered form
    values = {'_roles': [str(r.name) for r in request.user.get_roles()]}
    rvalue['form'] = item_form.render(page=get_current_form_page(clazz,
                                                                 request),
                                      values=values,
                                      previous_values=previous_values)
    return rvalue


def rest_read(request, callback=None):
    """Returns a JSON object of a specific item of type clazz. The
    loaded item is determined by the id provided in the matchdict object
    of the current request.

    :request: Current request
    :callback: Current function which is called after the item has been read.
    :returns: JSON object.
    """
    clazz = request.context.__model__
    item = get_item_from_request(request)
    if callback is not None:
        item = callback(request, item)
    return JSONResponse(True, item)
