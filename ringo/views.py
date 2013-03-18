from pyramid.response import Response
from pyramid.view import view_config

from formbar.config import Config, load
from formbar.form import Form

from sqlalchemy.exc import DBAPIError

from ringo.model import (
    DBSession,
)

from ringo.models import (
    MyModel,
)

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


@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    try:
        one = DBSession.query(MyModel).filter(MyModel.name == 'one').first()
    except DBAPIError:
        return Response(conn_err_msg,
                        content_type='text/plain', status_int=500)
    return {'one': one, 'project': 'ringo'}

conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_ringo_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""
