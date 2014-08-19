import logging
from formbar.config import (
    Config,
    load,
    parse
)
from formbar.form import Form


from ringo.lib.security import has_role
from ringo.lib.helpers import get_path_to_form_config
from ringo.lib.renderer import add_renderers
from ringo.views.request import (
    get_item_from_request,
    get_current_form_page
)
from ringo.model.form import Form as BlobformForm
from ringo.model.mixins import (
    Owned,
    Logged,
    Versioned,
    Blobform
)

log = logging.getLogger(__name__)


def get_blobform_config(request, item, formname):
    """Helper function used in the create_ method to setup the create
    forms for blogform items. To create a new blogform item the
    creation is done in three steps:

    1. Stage 1: The user selects a form from a list
    2. Stage 2: The create dialog is rendered with the selected form
    3. Stage 3: The item is validated and saved.

    :request: current request
    :item: item to build the form
    :formname: name of the form in the formconfig
    :returns: formconfig, item used to build a form.

    """
    # First check if the fid parameter is provided
    fid = request.params.get('fid')
    blobform = request.params.get('blobforms')
    if fid:
        log.debug("Stage 3: User has submitted data to create a new item")
        setattr(item, 'fid', fid)
        formfactory = BlobformForm.get_item_factory()
        formconfig = Config(parse(formfactory.load(fid).definition))
        return item, formconfig.get_form(formname)
    elif blobform:
        log.debug("Stage 2: User has selected a blobform %s " % blobform)
        setattr(item, 'fid', blobform)
        formfactory = BlobformForm.get_item_factory()
        formconfig = Config(parse(formfactory.load(blobform).definition))
        return item, formconfig.get_form(formname)
    else:
        log.debug("Stage 1: User is selecting a blobform")
        modul = item.get_item_modul(request)
        formconfig = modul.get_form_config("blobform")
        return modul, formconfig


def get_rendered_ownership_form(request, readonly=None):
    """Returns the rendered logbook form for the item in the current
    request. If the item is not an instance of Owned, than an empty
    string is returned."""
    item = get_item_from_request(request)
    form = get_ownership_form(request, readonly)
    if isinstance(item, Owned):
        return form.render()
    else:
        return ""


def get_ownership_form(request, readonly=None):
    item = get_item_from_request(request)
    if (readonly is None and isinstance(item, Owned)):
        readonly = not (item.is_owner(request.user)
                        or has_role(request.user, "admin"))
    config = Config(load(get_path_to_form_config('ownership.xml', 'ringo')))
    if readonly:
        form_config = config.get_form('ownership-form-read')
    else:
        form_config = config.get_form('ownership-form-update')
    return Form(form_config, item, request.db,
                csrf_token=request.session.get_csrf_token(),
                eval_url='/rest/rule/evaluate')


def get_rendered_logbook_form(request, readonly=None):
    """Returns the rendered logbook form for the item in the current
    request. If the item is not an instance of Owned, than an empty
    string is returned."""
    item = get_item_from_request(request)
    form = get_logbook_form(request, readonly)
    if isinstance(item, Logged):
        return form.render()
    else:
        return ""


def get_logbook_form(request, readonly=None):
    item = get_item_from_request(request)
    config = Config(load(get_path_to_form_config('logbook.xml', 'ringo')))
    if readonly:
        form_config = config.get_form('logbook-form-read')
    else:
        form_config = config.get_form('logbook-form-update')
    renderers = add_renderers({})
    return Form(form_config, item, request.db,
                renderers=renderers,
                csrf_token=request.session.get_csrf_token(),
                eval_url='/rest/rule/evaluate')


def get_rendered_item_form(name, request, values=None, renderers=None):
    """Returns the rendered logbook form for the item in the current
    request. If the item is not an instance of Owned, than an empty
    string is returned."""
    if not values:
        values = {}
    if not renderers:
        renderers = {}
    clazz = request.context.__model__
    item = get_item_from_request(request)
    name = request.session.get("%s.form" % clazz) or name
    form = get_item_form(name, request, renderers)
    if isinstance(item, Versioned):
        previous_values = item.get_previous_values(author=request.user.login)
    else:
        previous_values = {}
    # Validate the form to generate the warnings if the form has not
    # been alreaded validated.
    if not form.validated:
        form.validate(None)
    page = get_current_form_page(clazz, request)
    # Add ringo specific values into the renderered form
    return form.render(page=page, values=values,
                       previous_values=previous_values)


def get_item_form(name, request, renderers=None):
    """Will return a form for the given item

    :name: Name of the form
    :request: Current request
    :renderers: Dictionary with custom renderers
    :returns: Form
    """
    item = get_item_from_request(request)
    if not renderers:
        renderers = {}
    renderers = add_renderers(renderers)
    clazz = request.context.__model__
    name = request.session.get("%s.form" % clazz) or name

    ## handle blobforms
    if isinstance(item, Blobform):
        item, formconfig = get_blobform_config(request, item, name)
    else:
        formconfig = item.get_form_config(name)

    form = Form(formconfig, item, request.db,
                translate=request.translate,
                renderers=renderers,
                change_page_callback={'url': 'set_current_form_page',
                                      'item': clazz.__tablename__,
                                      'itemid': item.id},
                request=request,
                csrf_token=request.session.get_csrf_token(),
                eval_url='/rest/rule/evaluate')
    return form
