from pyramid.security import remember, forget
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from formbar.config import Config, load
from formbar.form import Form

from ringo.lib.helpers import get_path_to_form_config
from ringo.lib.security import login as user_login, request_password_reset


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
    config = Config(load(get_path_to_form_config('auth.xml')))
    form_config = config.get_form('forgot_password')
    form = Form(form_config)
    if request.POST:
        if form.validate(request.params.mixed()):
            username = form.data.get('login')
            token = request_password_reset(username)
            if token:
                # Generate email with the password request token.
                pass
            target_url = request.route_url('login')
            headers = forget(request)
            msg = _("Password reset token has been sent to the users "
                    "email address. Please check your email :)")
            request.session.flash(msg, 'success')
            return HTTPFound(location=target_url, headers=headers)
    return {'form': form.render()}
