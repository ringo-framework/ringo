from ringo.lib.security import has_role
from ringo.lib.helpers import get_path_to_form_config
from ringo.lib.renderer import add_renderers
from ringo.views.request import get_item_from_request
from ringo.model.mixins import Owned

from formbar.config import Config, load
from formbar.form import Form


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


def get_logbook_form(request, readonly=None, renderers=None):
    item = get_item_from_request(request)
    if not renderers:
        renderers = {}
    renderers = add_renderers(renderers)
    config = Config(load(get_path_to_form_config('logbook.xml', 'ringo')))
    if readonly:
        form_config = config.get_form('logbook-form-read')
    else:
        form_config = config.get_form('logbook-form-update')
    return Form(form_config, item, request.db,
                renderers=renderers,
                csrf_token=request.session.get_csrf_token(),
                eval_url='/rest/rule/evaluate')


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
    form = Form(item.get_form_config(name), item, request.db,
                translate=request.translate,
                renderers=renderers,
                change_page_callback={'url': 'set_current_form_page',
                                      'item': clazz.__tablename__,
                                      'itemid': item.id},
                request=request,
                csrf_token=request.session.get_csrf_token(),
                eval_url='/rest/rule/evaluate')
    return form
