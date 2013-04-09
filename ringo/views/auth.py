from pyramid.security import remember, forget
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message


from formbar.config import Config, load
from formbar.form import Form

from ringo.lib.helpers import get_path_to_form_config
from ringo.lib.security import login as user_login, request_password_reset, \
    password_reset


@view_config(route_name='login', renderer='/auth/login.mako')
def login(request):
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
    _ = request.translate
    target_url = request.route_url('home')
    headers = forget(request)
    msg = _("Logout was successfull :)")
    request.session.flash(msg, 'success')
    return HTTPFound(location=target_url, headers=headers)


@view_config(route_name='forgot_password',
             renderer='/auth/forgot_password.mako')
def forgot_password(request):
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

                pass
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
