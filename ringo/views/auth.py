from pyramid.security import remember, forget
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from formbar.config import Config, load
from formbar.form import Form

from ringo.lib.helpers import get_path_to_form_config
from ringo.lib.security import login as user_login


@view_config(route_name='login', renderer='/auth/login.mako')
def login(request):
    config = Config(load(get_path_to_form_config('auth.xml')))
    form_config = config.get_form('loginform')
    form = Form(form_config)
    if request.POST:
        form.validate(request.params.mixed())
        username = form.data.get('login')
        password = form.data.get('pass')
        user = user_login(username, password)
        if user is None:
            msg = "Login failed!"
            request.session.flash(msg, 'error')
        else:
            msg = "Login was successfull :)"
            request.session.flash(msg, 'success')
            headers = remember(request, user.id, max_age='86400')
            target_url = request.route_url('home')
            return HTTPFound(location=target_url, headers=headers)
    return {'form': form.render()}


@view_config(route_name='logout', renderer='/auth/logout.mako')
def logout(request):
    target_url = request.route_url('home')
    headers = forget(request)
    msg = "Logout was successfull :)"
    request.session.flash(msg, 'success')
    return HTTPFound(location=target_url, headers=headers)
