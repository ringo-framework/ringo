import logging
import sqlalchemy as sa
from pyramid.httpexceptions import HTTPBadRequest, HTTPForbidden, HTTPFound
from pyramid.view import view_config
from formbar.form import Form, Validator

from ringo.views.base import create, rest_create
from ringo.views.helpers import get_current_form_page

from ringo.views.request import (
    handle_history,
    handle_params
)
from ringo.model.mixins import Owned

from ringo.lib.form import get_form_config
from ringo.lib.helpers import import_model, get_action_routename
from ringo.lib.security import login, encrypt_password
from ringo.lib.sql.cache import invalidate_cache
User = import_model('ringo.model.user.User')

log = logging.getLogger(__name__)

def user_create_callback(request, user):
    user = encrypt_password_callback(request, user)
    # Set profile data
    user.profile[0].first_name = request.params.get("first_name")
    user.profile[0].last_name = request.params.get("last_name")
    user.profile[0].email = request.params.get("email")
    return user

def encrypt_password_callback(request, user):
    """Callback helper function. This function is called within the base
    create view to encrypt the password after the user has been
    created."""
    unencryped_pw = user.password
    user.password = encrypt_password(unencryped_pw)
    return user

def check_password(field, data):
    """Validator function as helper for formbar validators"""
    password = data[field]
    username = data["login"]
    return bool(login(username, password))

###########################################################################
#                               HTML VIEWS                                #
###########################################################################


@view_config(route_name=get_action_routename(User, 'create'),
             renderer='/default/create.mako',
             permission='create')
def create_(request):
    return create(request, user_create_callback)


@view_config(route_name=get_action_routename(User, 'changepassword'),
             renderer='/users/changepassword.mako')
def changepassword(request):
    """Method to change the users password by the user. The user user
    musst provide his old and the new pasword. Users are only allowed to
    change their own password."""
    clazz = User
    handle_history(request)
    handle_params(request)
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

    form = Form(get_form_config(item, 'changepassword'),
                item, request.db, translate=_,
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
            encrypt_password_callback(request, item)
            msg = _('Changed password for "${item}" successfull.',
                    mapping=mapping)
            log.info(msg)
            request.session.flash(msg, 'success')
            route_name = get_action_routename(item, 'changepassword')
            url = request.route_path(route_name, id=item.id)
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

@view_config(route_name=get_action_routename(User, 'create', prefix="rest"),
             renderer='json',
             request_method="POST",
             permission='create')
def rest_create_(request):
    return rest_create(User, request, user_create_callback)
