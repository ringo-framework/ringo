import logging
from pyramid.view import view_config

from ringo.views.base import list_, create_, update_, read_, delete_
from ringo.model.user import Usergroup

log = logging.getLogger(__name__)


@view_config(route_name=Usergroup.get_action_routename('list'),
             renderer='/default/list.mako')
def list(request):
    return list_(Usergroup, request)


@view_config(route_name=Usergroup.get_action_routename('create'),
             renderer='/default/create.mako')
def create(request):
    return create_(Usergroup, request)


@view_config(route_name=Usergroup.get_action_routename('update'),
             renderer='/default/update.mako')
def update(request):
    return update_(Usergroup, request)


@view_config(route_name=Usergroup.get_action_routename('read'),
             renderer='/default/read.mako')
def read(request):
    return read_(Usergroup, request)


@view_config(route_name=Usergroup.get_action_routename('delete'),
             renderer='/default/confirm.mako')
def delete(request):
    return delete_(Usergroup, request)
