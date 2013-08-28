import logging
import hashlib
from pyramid.view import view_config

from ringo.views.base import list_, create_, update_, read_, delete_
from ringo.views.json import (
    list_   as json_list,
    create_ as json_create,
    update_ as json_update,
    read_   as json_read,
    delete_ as json_delete
    )
from ringo.lib.helpers import import_model
User = import_model('ringo.model.user.User')

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

###########################################################################
#                               HTML VIEWS                                #
###########################################################################

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

###########################################################################
#                               REST SERVICE                              #
###########################################################################

@view_config(route_name=User.get_action_routename('list', prefix="rest"),
             renderer='json',
             request_method="GET",
             permission='list'
             )
def rest_list(request):
    return json_list(User, request)

@view_config(route_name=User.get_action_routename('create', prefix="rest"),
             renderer='json',
             request_method="POST",
             permission='create')
def rest_create(request):
    return json_create(User, request, encrypt_password)

@view_config(route_name=User.get_action_routename('read', prefix="rest"),
             renderer='json',
             request_method="GET",
             permission='read')
def rest_read(request):
    return json_read(User, request)

@view_config(route_name=User.get_action_routename('update', prefix="rest"),
             renderer='json',
             request_method="PUT",
             permission='update')
def rest_update(request):
    return json_update(User, request)

@view_config(route_name=User.get_action_routename('delete', prefix="rest"),
             renderer='json',
             request_method="DELETE",
             permission='delete')
def rest_delete(request):
    return json_delete(User, request)
