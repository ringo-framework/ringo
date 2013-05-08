import os
import logging
import pkg_resources
from pyramid.config import Configurator
from pyramid.events import BeforeRender, NewRequest
from pyramid_beaker import session_factory_from_settings

from sqlalchemy import engine_from_config

log = logging.getLogger(__name__)


from ringo.resources import (
    get_resource_factory,
)
from ringo.model import (
    DBSession,
    Base,
)
from ringo.model.user import (
    User,
    Profile,
    Usergroup,
    Role
)
from ringo.model.modul import (
    ModulItem,
    ActionItem,
)
from ringo.lib import (
    helpers,
    security
)
from ringo.lib.i18n import (
    locale_negotiator,
)

base_dir = pkg_resources.get_distribution("ringo").location
template_dir = os.path.join(base_dir, 'ringo', 'templates')


def add_renderer_globals(event):
    request = event['request']
    event['h'] = helpers
    event['s'] = security
    event['_'] = request.translate
    event['N_'] = request.translate
    event['localizer'] = request.localizer


def connect_on_request(event):
    request = event.request
    request.db = DBSession
    request.add_finished_callback(close_db_connection)


def close_db_connection(request):
    request.db.close()


def add_route(config, clazz):
    """Setup routes for the activates actions of the given modul.
    Therefor the modul will be loaded to get the configured actions. The
    new routes will be added with the following name and url:

    * Name: $modulname-$actionname
    * Url:  $modulname/$actionurl

    Note, that the actionname can be configured only as admin.

    Further a clazz specific factory will be added to the route which is
    later used to setup the ACL of items of the modul.

    :config: Pylons config instance
    :clazz: The clazz of the module for which the new routes will be set up.
    :returns: config

    """
    # load modul to get the enabled actions
    factory = ModulItem.get_item_factory()
    modul = factory.load(clazz._modul_id)
    name = clazz.__tablename__
    for action in modul.actions:
        route_name = "%s-%s" % (name, action.name.lower())
        route_url = "%s/%s" % (name, action.url)
        log.debug("Adding route: %s, %s" % (route_name, route_url))
        config.add_route(route_name, route_url,
                         factory=get_resource_factory(clazz))
    return config


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings,
                          locale_negotiator=locale_negotiator)
    config.set_session_factory(session_factory_from_settings(settings))
    config.include('pyramid_handlers')
    config.include('pyramid_beaker')
    config.include('ringo.lib.security.setup_ringo_security')
    config.add_subscriber(connect_on_request, NewRequest)
    config.add_subscriber(add_renderer_globals, BeforeRender)

    config.add_route('home', '/')
    config.add_route('login', 'auth/login')
    config.add_route('register_user', 'auth/register_user')
    config.add_route('confirm_user', 'auth/confirm_user/{token}')
    config.add_route('forgot_password', 'auth/forgot_password')
    config.add_route('reset_password', 'auth/reset_password/{token}')
    config.add_route('logout', 'auth/logout')

    # Modules admininistration
    add_route(config, ModulItem)
    add_route(config, ActionItem)
    # Users admininistration
    add_route(config, User)
    # Usergroups admininistration
    add_route(config, Usergroup)
    # Roles admininistration
    add_route(config, Role)
    # Profile admininistration
    add_route(config, Profile)

    config.add_translation_dirs('ringo:locale/')
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
