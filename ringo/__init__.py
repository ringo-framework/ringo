import os
import logging
from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings

from sqlalchemy import engine_from_config

log = logging.getLogger(__name__)


from ringo.resources import (
    get_resource_factory,
)
from ringo.lib.sql import (
    DBSession,
)
from ringo.model import (
    Base,
)
from ringo.model.base import (
    clear_cache,
)
from ringo.model.user import User
from ringo.model.modul import ModulItem
from ringo.model.news import News
from ringo.config import (
    write_formbar_static_files, static_dir, setup_modul
)
from ringo.lib import (
    helpers
)
from ringo.lib.i18n import (
    locale_negotiator,
)

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    clear_cache()
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings,
                          locale_negotiator=locale_negotiator)

    config.set_session_factory(session_factory_from_settings(settings))
    config.include('ringo')
    return config.make_wsgi_app()


def includeme(config):
    log.info('Setup of Ringo...')
    config.include('ringo.lib.i18n.setup_translation')
    config.include('ringo.lib.sql.db.setup_connect_on_request')
    config.include('ringo.lib.renderer.setup_render_globals')
    config.include('ringo.setup_pyramid_modules')
    config.include('ringo.lib.security.setup_ringo_security')
    config = setup_static_views(config)
    log.info('-> Static views finished.')
    config.include(setup_routes)
    log.info('-> Routes finished.')
    write_formbar_static_files()
    config.scan()
    log.info('OK :) Setup of Ringo finished.')

def setup_pyramid_modules(config):
    config.include('pyramid_handlers')
    config.include('pyramid_beaker')
    config.include('pyramid_mako')
    log.info('-> Modules finished.')
    return config

def setup_static_views(config):
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
    return config

def setup_routes(config):
    """Function which will setup the routes of the ringo application"""

    # SINGLE PAGES
    ##############
    config.add_route('login', 'auth/login')
    config.add_route('register_user', 'auth/register_user')
    config.add_route('confirm_user', 'auth/confirm_user/{token}')
    config.add_route('forgot_password', 'auth/forgot_password')
    config.add_route('reset_password', 'auth/reset_password/{token}')
    config.add_route('logout', 'auth/logout')
    config.add_route('version', 'version')
    config.add_route('contact', 'contact')
    config.add_route('about', 'about')
    config.add_route('home', '/')

    # MODULES
    #########
    # FIXME: Check why it is not possible to submit the loaded clazz in
    # the first for loop into the add_route method. It only seems only
    # to work after loading and saving the saving the modules in a dict.
    # Otherwise the views seems not not be mapped correctly to the routes.
    # (torsten) <2014-05-09 18:32>
    module_classes = {}
    for modul in DBSession.query(ModulItem).filter(ModulItem.id < 1000).all():
        clazz = helpers.dynamic_import(modul.clazzpath)
        module_classes[clazz._modul_id] = clazz
    for modul_id in module_classes:
        setup_modul(config, module_classes[modul_id])

    # Helpers
    #########
    config.add_route('set_current_form_page', 'set_current_form_page')
    config.add_route('users-changepassword',
                     'users/changepassword/{id}',
                     factory=get_resource_factory(User))
    config.add_route(News.get_action_routename('markasread', prefix="rest"),
                     'rest/news/{id}/markasread',
                     factory=get_resource_factory(News))
    config.add_route('rules-evaluate', 'rest/rule/evaluate')
    config.add_route('form-render', 'rest/form/render')

    return config
