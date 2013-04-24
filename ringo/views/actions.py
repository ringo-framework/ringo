import logging
from pyramid.view import view_config

from ringo.views.base import list_, create_, update_, read_, delete_
from ringo.model.modul import ActionItem

log = logging.getLogger(__name__)


@view_config(route_name=ActionItem.get_action_routename('list'),
             renderer='/default/list.mako',
             permission='list')
def list(request):
    return list_(ActionItem, request)


@view_config(route_name=ActionItem.get_action_routename('create'),
             renderer='/default/create.mako',
             permission='create')
def create(request):
    return create_(ActionItem, request)


@view_config(route_name=ActionItem.get_action_routename('update'),
             renderer='/default/update.mako',
             permission='update')
def update(request):
    return update_(ActionItem, request)


@view_config(route_name=ActionItem.get_action_routename('read'),
             renderer='/default/read.mako',
             permission='read')
def read(request):
    return read_(ActionItem, request)


@view_config(route_name=ActionItem.get_action_routename('delete'),
             renderer='/default/confirm.mako',
             permission='delete')
def delete(request):
    return delete_(ActionItem, request)
