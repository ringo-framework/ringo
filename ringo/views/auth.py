import hashlib
import uuid

from pyramid.security import remember, forget
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message


from ringo.model import DBSession
from ringo.model.base import BaseFactory
from ringo.model.user import User, Profile, Usergroup, USER_GROUP_ID
from formbar.config import Config, load
from formbar.form import Form, Validator

from ringo.views import handle_history
from ringo.lib.helpers import get_path_to_form_config
from ringo.lib.security import login as user_login, request_password_reset, \
    password_reset, activate_user


def is_login_unique(field, data):
    """Validator function as helper for formbar validators"""
    users = DBSession.query(User).filter_by(login=data[field]).all()
    return len(users) == 0


@view_config(route_name='login', renderer='/auth/login.mako')
def login(request):
    handle_history(request)
    _ = request.translate
    config = Config(load(get_path_to_form_config('auth.xml')))
    form_config = config.get_form('loginform')
    form = Form(form_config)
    if request.POST:
        form.validate(request.params.mixed())
        username = form.data.get('login')
        password = form.data.get('pass')
        user = user_login(username, password)
        if user is None:
            msg = _("Login failed!")
            request.session.flash(msg, 'error')
        else:
            msg = _("Login was successfull :)")
            request.session.flash(msg, 'success')
            headers = remember(request, user.id, max_age='86400')
            target_url = request.route_url('home')
            return HTTPFound(location=target_url, headers=headers)
    return {'form': form.render()}


@view_config(route_name='logout', renderer='/auth/logout.mako')
def logout(request):
    handle_history(request)
    _ = request.translate
    target_url = request.route_url('home')
    headers = forget(request)
    msg = _("Logout was successfull :)")
    request.session.flash(msg, 'success')
    return HTTPFound(location=target_url, headers=headers)


@view_config(route_name='register_user',
             renderer='/auth/register_user.mako')
def register_user(request):
    handle_history(request)
    _ = request.translate
    settings = request.registry.settings
    config = Config(load(get_path_to_form_config('auth.xml')))
    form_config = config.get_form('register_user')
    form = Form(form_config)
    # Do extra validation which is not handled by formbar.
    # Is the login unique?
    validator = Validator('login',
                          'There is already a user with this name',
                          is_login_unique)
    form.add_validator(validator)
    if request.POST:
        if form.validate(request.params.mixed()):
            # 1. Create user. Do not activate him. Default role is user.
            ufac = BaseFactory(User)
            pfac = BaseFactory(Profile)
            gfac = BaseFactory(Usergroup)
            user = ufac.create(None)
            # Set login from formdata
            user.login = form.data['login']
            # Encrypt password and save
            pw = hashlib.md5()
            pw.update(form.data['pass'])
            user.password = pw.hexdigest()
            # Deactivate the user. To activate the user needs to confirm
            # with the activation link
            user.activated = False
            atoken = str(uuid.uuid4())
            user.activation_token = atoken
            # Set user group
            group = gfac.load(USER_GROUP_ID)
            user.groups.append(group)
            # Set default user group.
            user.gid = group.id
            DBSession.add(user)
            profile = pfac.create(None)
            profile.email = form.data['email']
            profile.user = user
            DBSession.add(profile)
            # 3. Send confirmation email. The user will be activated
            #    after the user clicks on the confirmation link
            sender = settings['mail.default_sender']
            recipient = profile.email
            subject = _('Confirm user registration for ringo')
            message = _('Please confirm the user registration by clicking'
                        ' on the following link: %s'
                        % request.route_url('confirm_user',
                                            token=atoken))
            _send_mail(request, recipient, sender, subject, message)
            target_url = request.route_url('login')
            headers = forget(request)
            msg = _("User has been created and a confirmation mail was sent"
                    " to the users email adress. Please check your email :)")
            request.session.flash(msg, 'success')
            return HTTPFound(location=target_url, headers=headers)
    return {'form': form.render()}


@view_config(route_name='confirm_user',
             renderer='/auth/confirm_user.mako')
def confirm_user(request):
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
    handle_history(request)
    _ = request.translate
    settings = request.registry.settings
    config = Config(load(get_path_to_form_config('auth.xml')))
    form_config = config.get_form('forgot_password')
    form = Form(form_config)
    if request.POST:
        if form.validate(request.params.mixed()):
            username = form.data.get('login')
            user = request_password_reset(username, request.db)
            if user:
                # Generate email with the password request token.
                sender = settings['mail.default_sender']
                # TODO: Why profile is a InstrumentedList? For now take
                # the only profile of the user
                recipient = user.profile[0].email
                subject = _('Password reset request for xxx')
                message = "Visit this URL to confirm a password reset: %s" \
                          % request.route_url('reset_password',
                                              token=user.reset_tokens[-1])
                _send_mail(request, recipient, sender, subject, message)
            target_url = request.route_url('login')
            headers = forget(request)
            msg = _("Password reset token has been sent to the users "
                    "email address. Please check your email :)")
            request.session.flash(msg, 'success')
            return HTTPFound(location=target_url, headers=headers)
    return {'form': form.render()}


@view_config(route_name='reset_password',
             renderer='/auth/reset_password.mako')
def reset_password(request):
    handle_history(request)
    _ = request.translate
    settings = request.registry.settings
    success = False
    token = request.matchdict.get('token')
    user, password = password_reset(token, request.db)
    if password:
        success = True
        # Generate email with the password request token.
        sender = settings['mail.default_sender']
        recipient = user.profile[0].email
        subject = _('Password has been resetted')
        message = "Your password has been resetted tp: %s" % password
        _send_mail(request, recipient, sender, subject, message)
        msg = _("Password has been successfull resetted. "
                "The new password was sent to the users email address."
                " Please check your email.")
    else:
        msg = _("Password was not resetted. Maybe the request"
                " token was not valid?")
    return {'msg': msg, 'success': success}


def _send_mail(request, recipient, sender, subject, message):
    """Will send and email with the subject and body to the recipient
    from the sender

    :recipient: The recipients mail address
    :sender: The senders mail address
    :subject: String of subject
    :message: Mails body.
    :returns: True or False

    """
    message = Message(subject=subject,
                      sender=sender,
                      recipients=[recipient],
                      body=message)
    mailer = get_mailer(request)
    mailer.send(message)
