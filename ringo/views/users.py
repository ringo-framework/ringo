import logging
import hashlib
from pyramid.view import view_config

from ringo.views.base import list_, create_, update_, read_, delete_
from ringo.model.user import User

log = logging.getLogger(__name__)


def encrypt_password(request, user):
    """Callback helper function. This function is called within the base
    create view to encrypt the password after the user has been
    created."""
    unencryped_pw = user.password
    pw = hashlib.md5()
    pw.update(unencryped_pw)
    user.password = pw.hexdigest()
    return user


@view_config(route_name=User.get_action_routename('list'),
             renderer='/default/list.mako',
             permission='list')
def list(request):
    return list_(User, request)


@view_config(route_name=User.get_action_routename('create'),
             renderer='/default/create.mako',
             permission='create')
def create(request):
    return create_(User, request, encrypt_password)


@view_config(route_name=User.get_action_routename('update'),
             renderer='/default/update.mako',
             permission='update')
def update(request):
    return update_(User, request)


@view_config(route_name=User.get_action_routename('read'),
             renderer='/default/read.mako',
             permission='read')
def read(request):
    return read_(User, request)


@view_config(route_name=User.get_action_routename('delete'),
             renderer='/default/confirm.mako',
             permission='delete')
def delete(request):
    return delete_(User, request)
