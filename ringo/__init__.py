from pyramid.config import Configurator
from pyramid.events import BeforeRender

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


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.add_subscriber(add_renderer_globals, BeforeRender)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('login', 'auth/login')
    config.add_route('logout', 'auth/logout')
    config.scan()
    return config.make_wsgi_app()
