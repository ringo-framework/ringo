import logging
from formbar.form import Form
from ringo.lib.form import get_form_config
from ringo.views.response import JSONResponse
from ringo.views.helpers import (
    get_item_form,
    render_item_form,
)
from ringo.views.request import (
    handle_params,
    handle_history,
    handle_POST_request,
    handle_redirect_on_success,
    get_return_value
)

log = logging.getLogger(__name__)


def create(request, callback=None, renderers=None,
           validators=None, values=None):
    """Base method to handle create requests. This view will render a
    create form to update items on (GET) requests.

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
    params = handle_params(request)

    # Create a new item
    clazz = request.context.__model__
    try:
        factory = clazz.get_item_factory(request)
    except TypeError:
        # Old version of get_item_factory method which does not take an
        # request parameter.
        factory = clazz.get_item_factory()
        factory._request = request
    # Only create a new item if there isn't already an item in the
    # request.context. This can happen if we define a custom view for
    # create where the item gets created before to set some default
    # values e.g (See create function of forms)
    if not request.context.item:
        request.context.item = factory.create(request.user, {})
    if values is None:
        values = {}
    values['_roles'] = [str(r.name) for r in request.user.roles]
    values.update(params.get('values', {}))

    #  FIXME: "form_values" seems to be only used in one single
    #  application (efa). For now we will leave this here to not break
    #  any things but it should be removed.
    #  See https://github.com/ringo-framework/ringo/issues/31
    #  (ti) <2016-10-18 21:51>
    form_values = request.session.get("form_values") or {}
    values.update(form_values)
    request.session["form_values"] = None
    request.session.save()

    form = get_item_form(params.get("form", "create"),
                         request, renderers, validators, values=values)
    if request.POST and 'blobforms' not in request.params:
        if handle_POST_request(form, request, callback, 'create', renderers):
            return handle_redirect_on_success(request)
    rvalues = get_return_value(request)
    rvalues['form'] = render_item_form(request, form, validate=False)
    return rvalues


def rest_create(request, callback=None):
    """Create a new item of type clazz. The item will be
    initialised with the data provided in the submitted POST request.
    The submitted data will be validated before the item is actually
    saved. If the submission fails the item is not saved in the
    database. In all cases the item is returned as JSON object with the
    item and updated values back to the client. The JSON Response will
    include further details on the reason why the validation failed.

    :clazz: Class of item to create
    :request: Current request
    :returns: JSON object.

    """
    clazz = request.context.__model__
    # Create a new item.
    factory = clazz.get_item_factory()
    item = factory.create(request.user)
    # Initialise the create form for the item to be able to validate the
    # submitted data.
    form = Form(get_form_config(item, 'create'),
                item, request.db, translate=request.translate,
                csrf_token=request.session.get_csrf_token())
    if form.validate(request.params):
            sitem = form.save()
            return JSONResponse(True, sitem)
    else:
        # Validation fails! return item
        return JSONResponse(False, sitem)
