# -*- coding: utf-8 -*-
import logging
import sqlalchemy as sa
import re
from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPForbidden,
    HTTPFound,
    HTTPUnauthorized
)
from pyramid.security import forget
from pyramid.view import view_config
from pyramid.compat import urlparse
from formbar.form import Form, Validator

from ringo.views.base import create, rest_create, update
from ringo.views.helpers import get_item_from_request, get_current_form_page

from ringo.views.request import (
    handle_caching
)

from ringo.lib.form import get_form_config
from ringo.lib.helpers import import_model, get_action_routename
from ringo.lib.security import verify_password, load_user, encrypt_password, has_permission
from ringo.lib.sql.cache import invalidate_cache

User = import_model('ringo.model.user.User')
Usergroup = import_model('ringo.model.user.Usergroup')
Role = import_model('ringo.model.user.Role')

log = logging.getLogger(__name__)


def user_create_callback(request, user):
    user = encrypt_password_callback(request, user)
    # Set profile data
    user.profile[0].first_name = request.params.get("_first_name")
    user.profile[0].last_name = request.params.get("_last_name")
    user.profile[0].email = request.params.get("_email")
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
    return verify_password(password, load_user(username).password)


def user_update_callback(request, user):
    """Will rename the users usergroup in case the login has been
    changed. This is needed as the name of the usergroup is the only we
    to find out which usergroup belongs to the user."""
    if hasattr(request, '_oldlogin') and user.login != request._oldlogin:
        usergroup = request.db.query(Usergroup).filter(
            Usergroup.name == request._oldlogin).first()
        # Handle case if the user user not have his own usergroup. This
        # is true for the default admin user e.g
        if usergroup:
            usergroup.name = user.login
    return user

###########################################################################
#                               HTML VIEWS                                #
###########################################################################


def user_name_create_validator(field, data, db):
    """Validator to ensure username uniqueness when creating users"""
    return db.query(User).filter(User.login == data[field]).count() == 0


def user_name_update_validator(field, data, params):
    """Validator to ensure username uniqueness when updating users"""
    db = params['db']

    # Only consider names for the other users
    return db.query(User).filter(User.login == data[field],
                                 ~(User.id == params['pk'])).count() == 0


def password_nonletter_validator(field, data):
    """Validator to ensure that passwords contain two non-letters"""
    return len(re.findall('[^a-zA-ZäöüÄÖÜß]', data[field])) >= 2


def password_minlength_validator(field, data):
    """Validator to ensure that passwords are at least 12 characters long."""
    return len(data[field]) >= 12


@view_config(route_name=get_action_routename(User, 'create'),
             renderer='/default/create.mako',
             permission='create')
def create_(request, callback=None):
    """View to create new users. This view also take a optional callback
    parameter which can be used to inject additional callbacks in case
    this view is owerwritten in another application.

    :request: Current request
    :callback: Optional paramter for callback(s)
    """

    callbacks = []
    callbacks.append(user_create_callback)
    if callback:
        if isinstance(callback, list):
            callbacks.extend(callback)
        else:
            callbacks.append(callback)

    _ = request.translate
    uniqueness_validator = Validator('login',
                                     _('This name is already in use, '
                                       'please use something unique.'),
                                     user_name_create_validator,
                                     request.db)
    pw_len_validator = Validator('password',
                                 _('Password must be at least 12 characters '
                                   'long.'),
                                 password_minlength_validator)
    pw_nonchar_validator = Validator('password',
                                     _('Password must contain at least 2 '
                                       'non-letters.'),
                                     password_nonletter_validator)
    return create(request, callbacks,
                  validators=[uniqueness_validator,
                              pw_len_validator,
                              pw_nonchar_validator])


@view_config(route_name=get_action_routename(User, 'update'),
             renderer='/default/update.mako',
             permission='update')
def update_(request, callback=None, renderers=None,
            validators=None, values=None):
    user = get_item_from_request(request)
    # Store the login name of the user in the request to make it
    # available in the callback
    request._oldlogin = user.login

    _ = request.translate
    uniqueness_validator = Validator('login',
                                     _('This name is already in use, '
                                       'please use something unique.'),
                                     user_name_update_validator,
                                     {'pk': user.id, 'db': request.db})
    pw_len_validator = Validator('password',
                                 _('Password must be at least 12 characters '
                                   'long.'),
                                 password_minlength_validator)
    pw_nonchar_validator = Validator('password',
                                     _('Password must contain at least 2 '
                                       'non-letters.'),
                                     password_nonletter_validator)

    if validators is None:
        validators = []
    validators.append(uniqueness_validator)
    validators.append(pw_len_validator)
    validators.append(pw_nonchar_validator)

    callbacks = []
    callbacks.append(user_update_callback)
    if callback:
        if isinstance(callback, list):
            callbacks.extend(callback)
        else:
            callbacks.append(callback)

    return update(request, values=values,
                  validators=validators, callback=callbacks)


@view_config(route_name=get_action_routename(Usergroup, 'setstandin'),
             renderer='/usergroups/setstandin.mako')
def setstandin(request, allowed_users=None):
    """Setting members in the default usergroup of the current user.
    Technically this is adding a standin for this user."""

    # Check authentification
    # As this view has now security configured it is
    # generally callable by all users. For this reason we first check if
    # the user is authenticated. If the user is not authenticated the
    # raise an 401 (unauthorized) exception.
    if not request.user:
        raise HTTPUnauthorized

    # Check authorisation
    # For normal users users shall only be allowed to set the standin
    # for their own usergroup. So check this and otherwise raise an exception.
    usergroup = get_item_from_request(request)
    if (usergroup.id != request.user.default_gid and
       not has_permission("update", usergroup, request)):
        raise HTTPForbidden()

    clazz = Usergroup
    request.session['%s.form' % clazz] = "membersonly"
    request.session.save()
    values = {}
    if allowed_users:
        values['_allowedusers'] = [u.login for u in allowed_users]

    # Result may be a HTTPFOUND object.
    result = update(request, values=values)
    if isinstance(result, dict):
        # If the standing is set by an administrational user then the id
        # of the usergroup´s user is stored in the the backurl.
        if request.GET.get('backurl'):
            user_id = urlparse.urlparse(
                request.GET.get('backurl')).path.split('/')[-1]
            user = request.db.query(User).get(user_id)
            if not user:
                raise HTTPBadRequest()
        # Otherwise the user sets the standin of his own group. In this
        # case the user is already in the request.
        else:
            user = request.user
        result['user'] = user

    # Reset form value in session
    handle_caching(request)
    return result


@view_config(route_name=get_action_routename(User, 'changepassword'),
             renderer='/users/changepassword.mako')
def changepassword(request):
    """Method to change the users password by the user. The user user
    musst provide his old and the new pasword. Users are only allowed to
    change their own password."""

    # Check authentification
    # As this view has now security configured it is
    # generally callable by all users. For this reason we first check if
    # the user is authenticated. If the user is not authenticated the
    # raise an 401 (unauthorized) exception.
    if not request.user:
        raise HTTPUnauthorized

    clazz = User
    _ = request.translate
    rvalue = {}
    # Load the item return 400 if the item can not be found.
    id = request.matchdict.get('id')
    factory = clazz.get_item_factory()
    try:
        item = factory.load(id, request.db)
        # Check authorisation
        # User are only allowed to set their own password.
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
        pw_len_validator = Validator('password',
                                     _('Password must be at least 12 '
                                       'characters long.'),
                                     password_minlength_validator)
        pw_nonchar_validator = Validator('password',
                                         _('Password must contain at least 2 '
                                           'non-letters.'),
                                         password_nonletter_validator)

        form.add_validator(validator)
        form.add_validator(pw_len_validator)
        form.add_validator(pw_nonchar_validator)
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


@view_config(route_name=get_action_routename(User, 'removeaccount'),
             renderer='/users/removeaccount.mako')
def removeaccount(request):
    """Method to remove the useraccout by the user."""

    # Check authentification
    # The view is only available for authenticated users and callable
    # if the user is not the admin unser (id=1)
    id = request.matchdict.get('id')
    if not request.user or id == '1':
        raise HTTPUnauthorized

    clazz = User
    _ = request.translate
    # Load the item return 400 if the item can not be found.
    factory = clazz.get_item_factory()
    try:
        item = factory.load(id, request.db)
        # Check authorisation
        if item.id != request.user.id:
            raise HTTPForbidden()
    except sa.orm.exc.NoResultFound:
        raise HTTPBadRequest()

    form = Form(get_form_config(item, 'removeaccount'),
                item, request.db, translate=_,
                renderers={},
                change_page_callback={'url': 'set_current_form_page',
                                      'item': clazz.__tablename__,
                                      'itemid': id},
                request=request, csrf_token=request.session.get_csrf_token())

    if request.POST:
        mapping = {'item': item}
        if form.validate(request.params):
            # Delete the account and redirect the user to a result page
            request.db.delete(item)
            headers = forget(request)
            target_url = request.route_path('users-accountremoved')
            return HTTPFound(location=target_url, headers=headers)
        else:
            msg = _('Deleting the account of '
                    '"${item}" failed.', mapping=mapping)
            log.info(msg)
            request.session.flash(msg, 'error')

    rvalue = {}
    rvalue['clazz'] = clazz
    rvalue['item'] = item
    rvalue['form'] = form.render(page=get_current_form_page(clazz, request))
    return rvalue


@view_config(route_name='users-accountremoved',
             renderer='/users/accountremoved.mako')
def accountremoved(request):
    return {}


def role_name_create_validator(field, data, db):
    """Validator to ensure username uniqueness when creating users"""
    return db.query(Role).filter(Role.name == data[field]).count() == 0


def role_name_update_validator(field, data, params):
    """Validator to ensure username uniqueness when updating users"""
    db = params['db']

    # Only consider names for the other users
    return db.query(Role).filter(Role.name == data[field],
                                 ~(Role.id == params['pk'])).count() == 0


@view_config(route_name=get_action_routename(Role, 'create'),
             renderer='/default/create.mako',
             permission='create')
def role_create_(request, callbacks=None):
    """View to create new roles.

    :request: Current request
    :callback: Optional paramter for callback(s)
    """

    _ = request.translate
    uniqueness_validator = Validator('name',
                                     _('This name is already in use, '
                                       'please use something unique.'),
                                     role_name_create_validator,
                                     request.db)
    return create(request, callbacks,
                  validators=[uniqueness_validator])


@view_config(route_name=get_action_routename(Role, 'update'),
             renderer='/default/update.mako',
             permission='update')
def role_update_(request, callback=None, renderers=None,
                 validators=None, values=None):
    role = get_item_from_request(request)
    # Store the name of the role in the request to make it
    # available in the callback
    request._oldname = role.name

    _ = request.translate
    uniqueness_validator = Validator('name',
                                     _('This name is already in use, '
                                       'please use something unique.'),
                                     role_name_update_validator,
                                     {'pk': role.id, 'db': request.db})
    if validators is None:
        validators = []
    validators.append(uniqueness_validator)

    callbacks = []
    if callback:
        if isinstance(callback, list):
            callbacks.extend(callback)
        else:
            callbacks.append(callback)

    return update(request, values=values,
                  validators=validators, callback=callbacks)


###########################################################################
#                               REST SERVICE                              #
###########################################################################


@view_config(route_name=get_action_routename(User, 'create', prefix="rest"),
             renderer='json',
             request_method="POST",
             permission='create')
def rest_create_(request):
    return rest_create(User, request, user_create_callback)
