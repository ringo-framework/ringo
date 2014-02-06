import logging
from pyramid.view import view_config

from ringo.views.base import list_, create_, update_, read_, delete_
from ringo.views.base import list_, create_, update_, read_, delete_,export_, import_
from ringo.views.json import (
    list_   as json_list,
    create_ as json_create,
    update_ as json_update,
    read_   as json_read,
    delete_ as json_delete
    )
from ringo.views.files import save_file
from ringo.model.printtemplate import Printtemplate

log = logging.getLogger(__name__)

#                                HTML VIEW                                #

@view_config(route_name=Printtemplate.get_action_routename('list'),
             renderer='/default/list.mako',
             permission='list')
def list(request):
    return list_(Printtemplate, request)


@view_config(route_name=Printtemplate.get_action_routename('create'),
             renderer='/default/create.mako',
             permission='create')
def create(request):
    return create_(Printtemplate, request, callback=save_file)


@view_config(route_name=Printtemplate.get_action_routename('update'),
             renderer='/default/update.mako',
             permission='update')
def update(request):
    return update_(Printtemplate, request, callback=save_file)


@view_config(route_name=Printtemplate.get_action_routename('read'),
             renderer='/default/read.mako',
             permission='read')
def read(request):
    return read_(Printtemplate, request)

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

@view_config(route_name=Printtemplate.get_action_routename('delete'),
             renderer='/default/confirm.mako',
             permission='delete')
def delete(request):
    return delete_(Printtemplate, request)


@view_config(route_name=Printtemplate.get_action_routename('export'),
             renderer='/default/export.mako',
             permission='export')
def export(request):
    return export_(Printtemplate, request)


@view_config(route_name=Printtemplate.get_action_routename('import'),
             renderer='/default/import.mako',
             permission='import')
def myimport(request):
    return import_(Printtemplate, request)

#                               REST SERVICE                              #

@view_config(route_name=Printtemplate.get_action_routename('list', prefix="rest"),
             renderer='json',
             request_method="GET",
             permission='list'
             )
def rest_list(request):
    return json_list(Printtemplate, request)

@view_config(route_name=Printtemplate.get_action_routename('create', prefix="rest"),
             renderer='json',
             request_method="POST",
             permission='create')
def rest_create(request):
    return json_create(Printtemplate, request, callback=save_file)

@view_config(route_name=Printtemplate.get_action_routename('read', prefix="rest"),
             renderer='json',
             request_method="GET",
             permission='read')
def rest_read(request):
    return json_read(Printtemplate, request)

@view_config(route_name=Printtemplate.get_action_routename('update', prefix="rest"),
             renderer='json',
             request_method="PUT",
             permission='update')
def rest_update(request):
    return json_update(Printtemplate, request, callback=save_file)

@view_config(route_name=Printtemplate.get_action_routename('delete', prefix="rest"),
             renderer='json',
             request_method="DELETE",
             permission='delete')
def rest_delete(request):
    return json_delete(Printtemplate, request)
