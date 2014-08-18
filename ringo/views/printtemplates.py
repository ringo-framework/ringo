import logging
from pyramid.view import view_config

from ringo.views.base import create, rest_create,  update, read_
from ringo.views.json import (
    update_ as json_update,
    )
from ringo.views.files import save_file
from ringo.model.printtemplate import Printtemplate

log = logging.getLogger(__name__)

#                                HTML VIEW                                #

@view_config(route_name=Printtemplate.get_action_routename('create'),
             renderer='/default/create.mako',
             permission='create')
def create_(request):
    return create_(request, callback=save_file)


@view_config(route_name=Printtemplate.get_action_routename('update'),
             renderer='/default/update.mako',
             permission='update')
def update(request):
    return update(request, callback=save_file)


@view_config(route_name=Printtemplate.get_action_routename('download'),
             permission='download')
def download(request):
    result = read_(Printtemplate, request)
    item = result['item']
    response = request.response
    response.content_type = str(item.mime)
    response.content_disposition = 'attachment; filename=%s' % item.name
    response.body = item.data
    return response

#                               REST SERVICE                              #

@view_config(route_name=Printtemplate.get_action_routename('create', prefix="rest"),
             renderer='json',
             request_method="POST",
             permission='create')
def rest_create_(request):
    return rest_create(request, callback=save_file)

@view_config(route_name=Printtemplate.get_action_routename('update', prefix="rest"),
             renderer='json',
             request_method="PUT",
             permission='update')
def rest_update(request):
    return json_update(Printtemplate, request, callback=save_file)
