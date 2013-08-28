import logging
from pyramid.view import view_config

from ringo.views.base import list_, update_, read_
from ringo.views.json import (
    list_   as json_list,
    update_ as json_update,
    read_   as json_read
    )
from ringo.lib.helpers import import_model
ModulItem = import_model('ringo.model.modul.ModulItem')

log = logging.getLogger(__name__)

###########################################################################
#                                HTML VIEW                                #
###########################################################################

@view_config(route_name=ModulItem.get_action_routename('list'),
             renderer='/default/list.mako',
             permission='list')
def list(request):
    return list_(ModulItem, request)


@view_config(route_name=ModulItem.get_action_routename('update'),
             renderer='/default/update.mako',
             permission='update')
def update(request):
    return update_(ModulItem, request)


@view_config(route_name=ModulItem.get_action_routename('read'),
             renderer='/default/read.mako',
             permission='read')
def read(request):
    return read_(ModulItem, request)

###########################################################################
#                             REST SERVICE                                #
###########################################################################

@view_config(route_name=ModulItem.get_action_routename('list', prefix="rest"),
             renderer='json',
             request_method="GET",
             permission='list'
             )
def rest_list(request):
    return json_list(ModulItem, request)

@view_config(route_name=ModulItem.get_action_routename('read', prefix="rest"),
             renderer='json',
             request_method="GET",
             permission='read')
def rest_read(request):
    return json_read(ModulItem, request)

@view_config(route_name=ModulItem.get_action_routename('update', prefix="rest"),
             renderer='json',
             request_method="PUT",
             permission='update')
def rest_update(request):
    return json_update(ModulItem, request)
