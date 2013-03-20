from pyramid.config import Configurator
from pyramid.events import BeforeRender, NewRequest
from pyramid_beaker import session_factory_from_settings

from sqlalchemy import engine_from_config


from ringo.model import (
    DBSession,
    Base,
)
from ringo.lib import (
    helpers,
)


def add_renderer_globals(event):
    event['h'] = helpers


def connect_on_request(event):
    request = event.request
    request.db = DBSession
    request.add_finished_callback(close_db_connection)


def close_db_connection(request):
    request.db.close()


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.set_session_factory(session_factory_from_settings(settings))
    config.include('pyramid_handlers')
    config.include('pyramid_beaker')
    config.include('ringo.lib.security.setup_ringo_security')
    config.add_subscriber(add_renderer_globals, BeforeRender)
    config.add_subscriber(connect_on_request, NewRequest)
    config.add_route('home', '/')
    config.add_route('login', 'auth/login')
    config.add_route('logout', 'auth/logout')

    # Users admininistration
    config.add_route('admin-users-list', 'users/list')
    config.add_route('admin-users-create', 'users/create')
    config.add_route('admin-users-update', 'users/update/{id}')
    config.add_route('admin-users-read', 'users/read/{id}')

    config.add_static_view('static',
                           path='ringo:static',
                           cache_max_age=3600)
    config.add_static_view('images',
                           path='ringo:static/images',
                           cache_max_age=3600)
    config.add_static_view('bootstrap',
                           path='ringo:static/bootstrap',
                           cache_max_age=3600)
    config.add_static_view('css',
                           path='ringo:static/css',
                           cache_max_age=3600)
    config.scan()
    return config.make_wsgi_app()
