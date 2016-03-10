import os
import logging
import pkg_resources
import transaction
from pyramid.events import NewRequest
from ringo.lib import helpers
from ringo.lib.extension import check_unregister_modul
from ringo.lib.sql.db import DBSession, NTDBSession
from ringo.lib.helpers import get_action_routename
from ringo.lib.form import get_formbar_css, get_formbar_js
from ringo.model.modul import ModulItem
from ringo.model import extensions
from ringo.model.mixins import Mixin
from ringo.model.base import get_item_list
from ringo.resources import get_resource_factory
from ringo.views.base import (
    web_action_view_mapping,
    rest_action_view_mapping,
    get_action_view
)

log = logging.getLogger(__name__)

def preload_modules(event):
    """Preload all modules on each request and put them into the request
    cache for the modules to save additional SQL queries as the modules
    are needed anyway."""
    for modul in get_item_list(event.request, ModulItem):
        event.request.cache_item_modul.set(modul.id, modul)

def setup(config):
    """Setup method which is called on application initialition and
    takes care that many ringo specific things are setup correctly."""

    # Trigger loading the static files of formbar and make them
    # available in global vars.
    # TODO: Move this call into a better place. (ti) <2015-07-28 13:19> 
    get_formbar_css() # -> formbar_css_filenames
    get_formbar_js() # -> formbar_js_filenames

    setup_extensions(config)
    setup_modules(config)
    config.include('ringo.lib.i18n.setup_translation')
    config.include('ringo.lib.sql.db.setup_session_on_request')
    config.include('ringo.lib.renderer.setup_render_globals')
    config.include('ringo.lib.security.setup_ringo_security')
    config.include('ringo.lib.cache.setup_cache')
    config.add_subscriber(preload_modules, NewRequest)


def setup_extensions(config):
    """Will setup the configured extensions. This included initialising
    new extension and removing extension which aren't configured any
    longer in the application."""
    # First initialise extenstion
    for extension in extensions:
        config.include(extension)
    # Now delete all extensions which are not configured.
    for modul in DBSession.query(ModulItem).all():
        check_unregister_modul(modul, extensions)


def setup_modules(config):
    """Will iterate over all configured modules in the application.
    Configured modules are loaded from database. For each module it will
    call the setup_modul method."""
    for modul in NTDBSession.query(ModulItem).all():
        setup_modul(config, modul)


def _setup_web_action(config, action, clazz, view_mapping):
    """Setup a route and a view for given action and clazz.
    The routes will have the follwoing following name and url:

    * Name: $modulname-$actionname
    * Url:  $modulname/$actionurl

    Note, that the actionname can be configured only as admin.

    Further a clazz specific factory will be added to the route which is
    later used to setup the ACL of items of the modul.

    :config: Configuration
    :action: Action item
    :clazz: clazz item
    :view_mapping: Dictionary with action items
    :returns: @todo
    """
    name = clazz.__tablename__
    action_name = action.name.lower()
    route_name = get_action_routename(clazz, action_name)
    route_url = "%s/%s" % (name, action.url)
    log.debug("Adding WEB route: %s, %s" % (route_name, route_url))
    config.add_route(route_name, route_url,
                     factory=get_resource_factory(clazz))
    settings = config.registry.settings
    http_cache = settings.get('security.page_http_cache', '0')
    view_func = get_action_view(view_mapping,
                                  action_name,
                                  name)
    if view_func:
        if action_name == "delete":
            template = "confirm"
            renderer = '/default/%s.mako' % template
        elif action_name == "download":
            renderer = None
        else:
            template = action_name
            renderer = '/default/%s.mako' % template
        config.add_view(view_func,
                        route_name=route_name,
                        renderer=renderer,
                        permission=action.permission or action_name,
                        http_cache=int(http_cache))
    ## Add bundle action.
    if action_name == "list":
       action_name = "bundle"
       route_name = "%s-%s" % (name, action_name)
       route_url = "%s/%s" % (name, action_name)
       view_func = get_action_view(view_mapping,
                                     action_name,
                                     name)
       log.debug("Adding route: %s, %s" % (route_name, route_url))
       config.add_route(route_name, route_url,
                        factory=get_resource_factory(clazz))
       config.add_view(view_func, route_name=route_name,
                       renderer='/default/bundle.mako',
                       permission='list')
    ## Add permission action.
    if action_name == "read":
        action_name = "ownership"
        route_name = "%s-%s" % (name, action_name)
        route_url = "%s/%s/{id}" % (name, action_name)
        view_func = get_action_view(view_mapping,
                                    action_name,
                                    name)
        log.debug("Adding route: %s, %s" % (route_name, route_url))
        config.add_route(route_name, route_url,
                         factory=get_resource_factory(clazz))
        config.add_view(view_func, route_name=route_name,
                        renderer='/default/update.mako',
                        permission='read')



def _setup_rest_action(config, action, clazz, view_mapping):
    """Setup a route and a view for given action and clazz.
    The routes will have the follwoing following name and url:

    * Name: $modulname-$actionname
    * Url:  $modulname/$actionurl

    Note, that the actionname can be configured only as admin.

    Further a clazz specific factory will be added to the route which is
    later used to setup the ACL of items of the modul.

    :config: Configuration
    :action: Action item
    :clazz: clazz item
    :view_mapping: Dictionary with action items
    :returns: @todo
    """
    action_method_mapping = {
        "list": "GET",
        "create": "POST",
        "read": "GET",
        "update": "PUT",
        "delete": "DELETE"
    }
    name = clazz.__tablename__
    action_name = action.name.lower()
    view_func = get_action_view(view_mapping,
                                  action_name,
                                  name)
    if not view_func:
        return
    route_name = get_action_routename(clazz, action_name,
                                      prefix="rest")
    tmpurl = action.url.split("/")
    if len(tmpurl) > 1:
        route_url = "rest/%s/%s" % (name, tmpurl[1])
    else:
        route_url = "rest/%s" % (name)
    log.debug("Adding REST route: %s, %s" % (route_name, route_url))
    method = action_method_mapping[action_name]
    config.add_route(route_name, route_url,
                     request_method=method,
                     factory=get_resource_factory(clazz))
    log.debug("Adding REST view: %s, %s, %s" % (view_func, route_name, method))
    settings = config.registry.settings
    http_cache = settings.get('security.page_http_cache', '0')
    config.add_view(view_func,
                    route_name=route_name,
                    request_method=method,
                    renderer='json',
                    permission=action.permission or action_name,
                    http_cache=int(http_cache))


def setup_modul(config, modul):
    """Setup routes and views for the activated actions of the given
    model of the modul.

    :config: Pylons config instance
    :modul: The module for which the new routes will be set up.
    """
    clazz = helpers.dynamic_import(modul.clazzpath)
    log.info("Setup modul '%s'" % modul.name)

    # Reload modul
    old_actions = list(a.url for a in modul.actions)

    for bclazz in clazz.__bases__:
        if issubclass(bclazz, Mixin):
            for action in bclazz.get_mixin_actions():
                if not action.url in old_actions:
                    action.mid = clazz._modul_id
                    modul.actions.append(action)
                    NTDBSession.add(action)
    NTDBSession.commit()

    for action in modul.actions:
        _setup_web_action(config, action, clazz, web_action_view_mapping)
        _setup_rest_action(config, action, clazz, rest_action_view_mapping)
