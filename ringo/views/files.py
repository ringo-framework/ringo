import logging
from pyramid.view import view_config

from ringo.views.base import list_, create_, update_, read_, delete_
from ringo.views.json import (
    list_   as json_list,
    create_ as json_create,
    update_ as json_update,
    read_   as json_read,
    delete_ as json_delete
    )
from ringo.model.file import File

log = logging.getLogger(__name__)

#                                HTML VIEW                                #

@view_config(route_name=File.get_action_routename('list'),
             renderer='/default/list.mako',
             permission='list')
def list(request):
    return list_(File, request)


@view_config(route_name=File.get_action_routename('create'),
             renderer='/default/create.mako',
             permission='create')
def create(request):
    return create_(File, request)


@view_config(route_name=File.get_action_routename('update'),
             renderer='/default/update.mako',
             permission='update')
def update(request):
    return update_(File, request)


@view_config(route_name=File.get_action_routename('read'),
             renderer='/default/read.mako',
             permission='read')
def read(request):
    return read_(File, request)


@view_config(route_name=File.get_action_routename('delete'),
             renderer='/default/confirm.mako',
             permission='delete')
def delete(request):
    return delete_(File, request)

#                               REST SERVICE                              #

@view_config(route_name=File.get_action_routename('list', prefix="rest"),
             renderer='json',
             request_method="GET",
             permission='list'
             )
def rest_list(request):
    return json_list(File, request)

@view_config(route_name=File.get_action_routename('create', prefix="rest"),
             renderer='json',
             request_method="POST",
             permission='create')
def rest_create(request):
    return json_create(File, request, encrypt_password)

@view_config(route_name=File.get_action_routename('read', prefix="rest"),
             renderer='json',
             request_method="GET",
             permission='read')
def rest_read(request):
    return json_read(File, request)

@view_config(route_name=File.get_action_routename('update', prefix="rest"),
             renderer='json',
             request_method="PUT",
             permission='update')
def rest_update(request):
    return json_update(File, request)

@view_config(route_name=File.get_action_routename('delete', prefix="rest"),
             renderer='json',
             request_method="DELETE",
             permission='delete')
def rest_delete(request):
    return json_delete(File, request)
