import uuid
import logging

import pyramid.httpexceptions as exc
from pyramid.security import remember, forget
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from formbar.config import Config, load
from formbar.form import Form, Validator

from ringo.lib.sql import DBSession
from ringo.model.user import USER_GROUP_ID, USER_ROLE_ID
from ringo.lib.helpers import import_model
from ringo.views.users import (
    password_minlength_validator,
    password_nonletter_validator
)
from ringo.lib.helpers.appinfo import get_app_title
from ringo.lib.helpers.misc import dynamic_import
from ringo.lib.form import get_path_to_form_config
from ringo.lib.security import login as user_login, request_password_reset, \
    password_reset, activate_user, encrypt_password, AuthentificationException
from ringo.lib.message import Mailer, Mail

User = import_model('ringo.model.user.User')
Usergroup = import_model('ringo.model.user.Usergroup')
Role = import_model('ringo.model.user.Role')

log = logging.getLogger(__name__)


def is_login_unique(field, data):
    """Validator function as helper for formbar validators"""
    users = DBSession.query(User).filter_by(login=data[field]).all()
    return len(users) == 0


def is_registration_enabled(settings):
    return (bool(settings.get('mail.host')) and
            bool(settings.get('mail.default_sender')) and
            settings.get('auth.register_user') == "true")


def is_pwreminder_enabled(settings):
    return (bool(settings.get('mail.host')) and
            bool(settings.get('mail.default_sender')) and
            settings.get('auth.password_reminder') == "true")


def is_authcallback_enabled(settings):
    return bool(settings.get('auth.callback'))


@view_config(route_name='login', renderer='/auth/login.mako')
def login(request):
    _ = request.translate
    settings = request.registry.settings
    config = Config(load(get_path_to_form_config('auth.xml')))
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
        elif not user.activated:
            msg = _("Login failed!")
            request.session.flash(msg, 'error')
            target_url = request.route_path('accountdisabled')
            return HTTPFound(location=target_url)
        else:

            # Handle authentication callback.
            if is_authcallback_enabled(settings):
                authenticated = False
                try:
                    callback = dynamic_import(settings.get("auth.callback"))
                    callback(request, user)
                    authenticated = True
                except AuthentificationException as e:
                    msg = e.message
                    request.session.flash(msg, 'critical')
            else:
                authenticated = True

            if authenticated:
                # Delete old session data and begin with new fresh session.
                request.session.invalidate()

                msg = _("Login was successfull")
                request.session.flash(msg, 'success')
                headers = remember(request, user.id)
                target_url = request.route_path('home')
                return HTTPFound(location=target_url, headers=headers)

    return {'form': form.render(),
            'registration_enabled': is_registration_enabled(settings),
            'pwreminder_enabled': is_pwreminder_enabled(settings)}


@view_config(route_name='logout', renderer='/auth/logout.mako')
def logout(request):
    _ = request.translate
    target_url = request.route_path('home')
    if request.params.get('autologout'):
        target_url = request.route_path('autologout')
        return HTTPFound(location=target_url)
    elif request.user:
        log.info("Logout successfull '%s'" % (request.user.login))
        msg = _("Logout was successfull")
        headers = forget(request)
        request.session.flash(msg, 'success')
        return HTTPFound(location=target_url, headers=headers)
    return HTTPFound(location=target_url)


@view_config(route_name='autologout', renderer='/auth/autologout.mako')
def autologout(request):

    # For the first call the user is still authenticated. So
    # delete the auth cookie and trigger a redirect calling the same
    # page.
    if request.user:
        headers = forget(request)
        target_url = request.route_path('autologout')
        if request.user.login != request.registry.settings.get("auth.anonymous_user"):
            log.info("Autologout successfull '%s'" % (request.user.login))
        return HTTPFound(location=target_url, headers=headers)
    # User is not authenticated here anymore. So simply render the
    # logout page.
    _ = request.translate
    return {"_": _}


@view_config(route_name='accountdisabled', renderer='/auth/disabled.mako')
def accountdisabled(request):
    _ = request.translate
    return {"_": _}


@view_config(route_name='register_user',
             renderer='/auth/register_user.mako')
def register_user(request):
    settings = request.registry.settings
    if not is_registration_enabled(settings):
        raise exc.exception_response(503)
    _ = request.translate
    config = Config(load(get_path_to_form_config('auth.xml')))
    form_config = config.get_form('register_user')
    form = Form(form_config, csrf_token=request.session.get_csrf_token(),
                translate=_)
    # Do extra validation which is not handled by formbar.
    # Is the login unique?
    login_unique_validator = Validator('login',
                                       _('There is already a user with this '
                                         'name'),
                                       is_login_unique)
    pw_len_validator = Validator('pass',
                                 _('Password must be at least 12 characters '
                                   'long.'),
                                 password_minlength_validator)
    pw_nonchar_validator = Validator('pass',
                                     _('Password must contain at least 2 '
                                       'non-letters.'),
                                     password_nonletter_validator)
    form.add_validator(login_unique_validator)
    form.add_validator(pw_len_validator)
    form.add_validator(pw_nonchar_validator)
    registration_complete = False
    if request.POST:
        if form.validate(request.params):
            # 1. Create user. Do not activate him. Default role is user.
            ufac = User.get_item_factory()
            user = ufac.create(None, form.data)
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
            user.profile[0].email = form.data['_email']

            # 2. Set user group
            gfac = Usergroup.get_item_factory()
            default_grps = settings.get("auth.register_user_default_groups",
                                        str(USER_GROUP_ID))
            for gid in [int(id) for id in default_grps.split(",")]:
                group = gfac.load(gid)
                user.groups.append(group)

            # 3. Set user role
            rfac = Role.get_item_factory()
            default_roles = settings.get("auth.register_user_default_roles",
                                         str(USER_ROLE_ID))
            for rid in [int(id) for id in default_roles.split(",")]:
                role = rfac.load(rid)
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
                      'login': user.login,
                      '_': _}
            mail = Mail([recipient],
                        subject,
                        template="register_user",
                        values=values)
            mailer.send(mail)

            msg = _("User has been created and a confirmation mail was sent"
                    " to the users email adress. Please check your email.")
            request.session.flash(msg, 'success')
            registration_complete = True
    return {'form': form.render(), 'complete': registration_complete}


@view_config(route_name='confirm_user',
             renderer='/auth/confirm_user.mako')
def confirm_user(request):
    settings = request.registry.settings
    if not is_registration_enabled(settings):
        raise exc.exception_response(503)
    _ = request.translate
    success = False
    token = request.matchdict.get('token')
    user = activate_user(token, request.db)
    if user:
        success = True
        msg = _("The user has beed successfull confirmed.")
    else:
        msg = _("The user was not confirmed. Maybe the confirmation"
                " token was not valid or the user is already confirmed?")
    return {'msg': msg, 'success': success}


@view_config(route_name='forgot_password',
             renderer='/auth/forgot_password.mako')
def forgot_password(request):
    settings = request.registry.settings
    if not is_pwreminder_enabled(settings):
        raise exc.exception_response(503)
    _ = request.translate
    config = Config(load(get_path_to_form_config('auth.xml')))
    form_config = config.get_form('forgot_password')
    form = Form(form_config, csrf_token=request.session.get_csrf_token(),
                translate=_)
    complete = False
    msg = None
    if request.POST:
        if form.validate(request.params):
            username = form.data.get('login')
            user = request_password_reset(username, request.db)
            if user and user.profile[0].email:
                recipient = user.profile[0].email
                mailer = Mailer(request)
                token = user.reset_tokens[-1]
                subject = _('Password reset request')
                values = {'url': request.route_url('reset_password',
                                                   token=token),
                          'app_name': get_app_title(),
                          'email': settings['mail.default_sender'],
                          'username': username,
                          '_': _}
                mail = Mail([recipient],
                            subject,
                            template="password_reset_request",
                            values=values)
                mailer.send(mail)
                log.info(u"Passwort reset token sent to "
                         u"user {} with email {}".format(username, recipient))
            else:
                log.info(u"Failed sending Passwort reset token for {}. "
                         u"User not found or missing email".format(username))
            # Return a message to the user which does not allow to get
            # information about the existence of a user.
            msg = _("If the user has been found together with configured "
                    "e-mail, a confirmation mail for resetting the password "
                    "has been sent. Please check your e-mail box.")
            request.session.flash(msg, 'success')
            complete = True
    return {'form': form.render(), 'complete': complete, 'msg': msg}


@view_config(route_name='reset_password',
             renderer='/auth/reset_password.mako')
def reset_password(request):
    settings = request.registry.settings
    if not is_pwreminder_enabled(settings):
        raise exc.exception_response(503)
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
        mail = Mail([recipient],
                    subject,
                    template="password_reminder",
                    values=values)
        mailer.send(mail)
        msg = _("Password was resetted and sent to the users email address."
                " Please check your email.")
        success = True
    else:
        msg = _("Password was not resetted. Maybe the request"
                " token was not valid?")
    return {'msg': msg, 'success': success}
