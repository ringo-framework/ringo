from pyramid.view import view_config

from formbar.config import Config, load
from formbar.form import Form

from ringo.lib.helpers import get_path_to_form_config


@view_config(route_name='login', renderer='/auth/login.mako')
def login(request):
    config = Config(load(get_path_to_form_config('auth.xml')))
    form_config = config.get_form('login')
    form = Form(form_config)
    if request.POST:
        # Load the user and redirect the user to the url where he comes
        # from
        pass
    else:
        pass
    return {'form': form.render()}


@view_config(route_name='logout', renderer='/auth/logout.mako')
def logout(request):
    return {'project': 'ringo'}
