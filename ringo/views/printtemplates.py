import logging
from pyramid.view import view_config

from ringo.lib.helpers import get_action_routename
from ringo.views.base import (
    create, rest_create,
    update, rest_update,
    read
)
from ringo.views.files import save_file
from ringo.model.printtemplate import Printtemplate

log = logging.getLogger(__name__)

#                                HTML VIEW                                #

@view_config(route_name=get_action_routename(Printtemplate, 'create'),
             renderer='/default/create.mako',
             permission='create')
def create_(request):
    return create(request, callback=save_file)


@view_config(route_name=get_action_routename(Printtemplate, 'update'),
             renderer='/default/update.mako',
             permission='update')
def update_(request):
    return update(request, callback=save_file)


@view_config(route_name=get_action_routename(Printtemplate, 'download'),
             permission='download')
def download(request):
    result = read(request)
    item = result['item']
    response = request.response
    response.content_type = str(item.mime)
    response.content_disposition = 'attachment; filename=%s' % item.name
    response.body = item.data
    return response

#                               REST SERVICE                              #

@view_config(route_name=get_action_routename(Printtemplate, 'create', prefix="rest"),
             renderer='json',
             request_method="POST",
             permission='create')
def rest_create_(request):
    return rest_create(request, callback=save_file)

@view_config(route_name=get_action_routename(Printtemplate, 'update', prefix="rest"),
             renderer='json',
             request_method="PUT",
             permission='update')
def rest_update_(request):
    return rest_update(request, callback=save_file)
