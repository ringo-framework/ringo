import logging
import hashlib
import sqlalchemy as sa
from pyramid.httpexceptions import HTTPBadRequest, HTTPForbidden, HTTPFound
from pyramid.view import view_config
from formbar.form import Form, Validator

from ringo.views.base import (list_, create_, update_, read_, delete_,
                              handle_history, handle_params,
                              get_current_form_page)
from ringo.model.mixins import Owned

from ringo.views.json import (
    list_   as json_list,
    create_ as json_create,
    update_ as json_update,
    read_   as json_read,
    delete_ as json_delete
    )
from ringo.lib.helpers import import_model
from ringo.lib.security import login
from ringo.lib.sql import invalidate_cache
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

def check_password(field, data):
    """Validator function as helper for formbar validators"""
    password = data[field]
    username = data["login"]
    return bool(login(username, password))

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


@view_config(route_name=User.get_action_routename('changepassword'),
             renderer='/users/changepassword.mako')
def changepassword(request):
    """Method to change the users password by the user. The user user
    musst provide his old and the new pasword. Users are only allowed to
    change their own password."""
    clazz = User
    handle_history(request)
    handle_params(clazz, request)
    _ = request.translate
    rvalue = {}

    # Load the item return 400 if the item can not be found.
    id = request.matchdict.get('id')
    factory = clazz.get_item_factory()
    try:
        item = factory.load(id, request.db)
        # Check if the user is allowed to change the password for the user.
        if item.id != request.user.id:
            raise HTTPForbidden()
    except sa.orm.exc.NoResultFound:
        raise HTTPBadRequest()

    form = Form(item.get_form_config('changepassword'), item, request.db, translate=_,
                renderers={},
                change_page_callback={'url': 'set_current_form_page',
                                      'item': clazz.__tablename__,
                                      'itemid': id},
                request=request, csrf_token=request.session.get_csrf_token())

    if request.POST:
        mapping = {'item': item}
        # Do extra validation which is not handled by formbar.
        # Is the provided old password correct?
        validator = Validator('oldpassword',
                              _('The given password is not correct'),
                              check_password)
        form.add_validator(validator)
        if form.validate(request.params):
            form.save()
            # Actually save the password. This is not done in the form
            # as the password needs to be encrypted.
            encrypt_password(request, item)
            msg = _('Changed password for "${item}" successfull.',
                    mapping=mapping)
            log.info(msg)
            request.session.flash(msg, 'success')
            route_name = item.get_action_routename('changepassword')
            url = request.route_url(route_name, id=item.id)
            # Invalidate cache
            invalidate_cache()
            return HTTPFound(location=url)
        else:
            msg = _('Error on changing the password for '
                    '"${item}".', mapping=mapping)
            log.info(msg)
            request.session.flash(msg, 'error')

    rvalue['clazz'] = clazz
    rvalue['item'] = item
    rvalue['form'] = form.render(page=get_current_form_page(clazz, request))
    return rvalue

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
