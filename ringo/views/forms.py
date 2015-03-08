import logging
from pyramid.view import view_config

from ringo.lib.helpers import get_action_routename
from ringo.lib.form import get_path_to_form_config
from ringo.views.base import create
from ringo.model.form import Form

log = logging.getLogger(__name__)


def load_config(path):
    data = ""
    with open(path) as f:
        data = f.read()
    return data


@view_config(route_name=get_action_routename(Form, 'create'),
             renderer='/default/create.mako',
             permission='create')
def create_(request):
    clazz = request.context.__model__
    factory = clazz.get_item_factory()
    form = factory.create(request.user, values={})
    definition = load_config(get_path_to_form_config("blobform_template.xml",
                                                     "ringo"))
    form.definition = definition
    request.context.item = form
    return create(request)
