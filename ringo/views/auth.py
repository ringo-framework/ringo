import uuid

import pyramid.httpexceptions as exc
from pyramid.security import remember, forget
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from formbar.config import Config, load
from formbar.form import Form, Validator

from ringo.lib.sql import DBSession
from ringo.model.user import USER_GROUP_ID, USER_ROLE_ID
from ringo.lib.helpers import import_model
User = import_model('ringo.model.user.User')
Usergroup = import_model('ringo.model.user.Usergroup')
Role = import_model('ringo.model.user.Role')

from ringo.views.request import handle_history
from ringo.lib.helpers.appinfo import get_app_title
from ringo.lib.form import get_path_to_form_config
from ringo.lib.security import login as user_login, request_password_reset, \
    password_reset, activate_user, encrypt_password
from ringo.lib.message import Mailer, Mail


def is_login_unique(field, data):
    """Validator function as helper for formbar validators"""
    users = DBSession.query(User).filter_by(login=data[field]).all()
    return len(users) == 0


def is_registration_enabled(settings):
    return (bool(settings.get('mail.host'))
            and settings.get('auth.register_user') == "true")


def is_pwreminder_enabled(settings):
    return (bool(settings.get('mail.host'))
            and settings.get('auth.password_reminder') == "true")


@view_config(route_name='login', renderer='/auth/login.mako')
def login(request):
    handle_history(request)
    _ = request.translate
    settings = request.registry.settings
    config = Config(load(get_path_to_form_config('auth.xml', 'ringo')))
    form_config = config.get_form('loginform')
    form = Form(form_config, csrf_token=request.session.get_csrf_token(),
                translate=_)
    if request.POST:
        form.validate(request.params)
        username = form.data.get('login')
        password = form.data.get('pass')
        user = user_login(username, password)
        if user is None:
            msg = _("Login failed!")
            request.session.flash(msg, 'error')
        else:
            msg = _("Login was successfull :)")
            request.session.flash(msg, 'success')
            headers = remember(request, user.id)
            target_url = request.route_path('home')
            return HTTPFound(location=target_url, headers=headers)

    return {'form': form.render(),
            'registration_enabled': is_registration_enabled(settings),
            'pwreminder_enabled': is_pwreminder_enabled(settings)}


@view_config(route_name='logout', renderer='/auth/logout.mako')
def logout(request):
    handle_history(request)
    _ = request.translate
    target_url = request.route_path('home')
    headers = forget(request)
    msg = _("Logout was successfull :)")
    request.session.flash(msg, 'success')
    return HTTPFound(location=target_url, headers=headers)

@view_config(route_name='autologout', renderer='/auth/autologout.mako')
def autologout(request):
    _ = request.translate
    return {"_": _}


@view_config(route_name='register_user',
             renderer='/auth/register_user.mako')
def register_user(request):
    settings = request.registry.settings
    if not is_registration_enabled(settings):
        raise exc.exception_response(503)
    handle_history(request)
    _ = request.translate
    config = Config(load(get_path_to_form_config('auth.xml', 'ringo')))
    form_config = config.get_form('register_user')
    form = Form(form_config, csrf_token=request.session.get_csrf_token(),
                translate=_)
    # Do extra validation which is not handled by formbar.
    # Is the login unique?
    validator = Validator('login',
                          'There is already a user with this name',
                          is_login_unique)
    form.add_validator(validator)
    if request.POST:
        if form.validate(request.params):
            # 1. Create user. Do not activate him. Default role is user.
            ufac = User.get_item_factory()
            user = ufac.create(None)
            # Set login from formdata
            user.login = form.data['login']
            # Encrypt password and save
            user.password = encrypt_password(form.data['pass'])
            # Deactivate the user. To activate the user needs to confirm
            # with the activation link
            user.activated = False
            atoken = str(uuid.uuid4())
            user.activation_token = atoken
            # Set profile data
            user.profile[0].email = form.data['email']

            # 2. Set user group
            gfac = Usergroup.get_item_factory()
            group = gfac.load(USER_GROUP_ID)
            user.groups.append(group)

            # 3. Set user role
            rfac = Role.get_item_factory()
            role = rfac.load(USER_ROLE_ID)
            user.roles.append(role)
            # Set default user group.
            request.db.add(user)

            # 4. Send confirmation email. The user will be activated
            #    after the user clicks on the confirmation link
            mailer = Mailer(request)
            recipient = user.profile[0].email
            subject = _('Confirm user registration')
            values = {'url': request.route_url('confirm_user', token=atoken),
                      'app_name': get_app_title(),
                      'email': settings['mail.default_sender'],
                      '_': _}
            mail = Mail([recipient], subject, template="register_user", values=values)
            mailer.send(mail)

            target_url = request.route_path('login')
            headers = forget(request)
            msg = _("User has been created and a confirmation mail was sent"
                    " to the users email adress. Please check your email :)")
            request.session.flash(msg, 'success')
            return HTTPFound(location=target_url, headers=headers)
    return {'form': form.render()}


@view_config(route_name='confirm_user',
             renderer='/auth/confirm_user.mako')
def confirm_user(request):
    settings = request.registry.settings
    if not is_registration_enabled(settings):
        raise exc.exception_response(503)
    handle_history(request)
    _ = request.translate
    success = False
    token = request.matchdict.get('token')
    user = activate_user(token, request.db)
    if user:
        success = True
        msg = _("The user has beed successfull confirmed.")
    else:
        msg = _("The user was not confirmed. Maybe the confirmation"
                " token was not valid?")
    return {'msg': msg, 'success': success}


@view_config(route_name='forgot_password',
             renderer='/auth/forgot_password.mako')
def forgot_password(request):
    settings = request.registry.settings
    if not is_pwreminder_enabled(settings):
        raise exc.exception_response(503)
    handle_history(request)
    _ = request.translate
    config = Config(load(get_path_to_form_config('auth.xml', 'ringo')))
    form_config = config.get_form('forgot_password')
    form = Form(form_config, csrf_token=request.session.get_csrf_token(),
                translate=_)
    if request.POST:
        if form.validate(request.params):
            username = form.data.get('login')
            user = request_password_reset(username, request.db)
            if user:
                mailer = Mailer(request)
                recipient = user.profile[0].email
                subject = _('Password reset request')
                values = {'url': request.route_url('reset_password', token=user.reset_tokens[-1]),
                          'app_name': get_app_title(),
                          'email': settings['mail.default_sender'],
                          '_': _}
                mail = Mail([recipient], subject, template="password_reset_request", values=values)
                mailer.send(mail)
            target_url = request.route_path('login')
            headers = forget(request)
            msg = _("Password reset token has been sent to the users "
                    "email address. Please check your email :)")
            request.session.flash(msg, 'success')
            return HTTPFound(location=target_url, headers=headers)
    return {'form': form.render()}


@view_config(route_name='reset_password',
             renderer='/auth/reset_password.mako')
def reset_password(request):
    settings = request.registry.settings
    if not is_pwreminder_enabled(settings):
        raise exc.exception_response(503)
    handle_history(request)
    _ = request.translate
    success = False
    token = request.matchdict.get('token')
    user, password = password_reset(token, request.db)
    if password:
        mailer = Mailer(request)
        recipient = user.profile[0].email
        subject = _('Password has been reseted')
        values = {'password': password,
                  'app_name': get_app_title(),
                  'email': settings['mail.default_sender'],
                  '_': _}
        mail = Mail([recipient], subject, template="password_reminder", values=values)
        mailer.send(mail)
        msg = _("Password was resetted and sent to the users email address."
                " Please check your email :)")
        success = True
    else:
        msg = _("Password was not resetted. Maybe the request"
                " token was not valid?")
    return {'msg': msg, 'success': success}
