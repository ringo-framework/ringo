import os
import logging
import pkg_resources
from ringo.lib import helpers
from ringo.lib.sql.db import DBSession
from ringo.model.modul import ModulItem
from ringo.resources import get_resource_factory

base_dir = pkg_resources.get_distribution("ringo").location
template_dir = os.path.join(base_dir, 'ringo', 'templates')
static_dir = os.path.join(base_dir, 'ringo', 'static')

# Directory with templates to generate views and models
modul_template_dir = os.path.join(base_dir, 'ringo', 'scripts', 'templates')

log = logging.getLogger(__name__)


def setup(config):
    """Setup method which is called on application initialition and
    takes care that many ringo specific things are setup correctly."""
    setup_modules(config)
    config.include('ringo.lib.i18n.setup_translation')
    config.include('ringo.lib.sql.db.setup_connect_on_request')
    config.include('ringo.lib.renderer.setup_render_globals')
    config.include('ringo.lib.security.setup_ringo_security')
    config.include('ringo.lib.cache.setup_cache')
    write_formbar_static_files()


def setup_modules(config):
    """Will iterate over all configured modules in the application.
    Configured modules are loaded from database. For each module it will
    call the setup_modul method."""
    # FIXME: Check why it is not possible to submit the loaded clazz in
    # the first for loop into the add_route method. It only seems only
    # to work after loading and saving the saving the modules in a dict.
    # Otherwise the views seems not not be mapped correctly to the routes.
    # (torsten) <2014-05-09 18:32>
    module_classes = {}
    for modul in DBSession.query(ModulItem).all():
        clazz = helpers.dynamic_import(modul.clazzpath)
        module_classes[clazz._modul_id] = clazz
    for modul_id in module_classes:
        setup_modul(config, module_classes[modul_id])


def setup_modul(config, clazz):
    """Setup routes and views for the activated actions of the given
    model of the modul.  The new routes will be added with the following
    name and url:

    * Name: $modulname-$actionname
    * Url:  $modulname/$actionurl

    Note, that the actionname can be configured only as admin.

    Further a clazz specific factory will be added to the route which is
    later used to setup the ACL of items of the modul.

    :config: Pylons config instance
    :clazz: The clazz of the module for which the new routes will be set up.
    :returns: config

    """
    from ringo.views.base import action_view_mapping as wavm
    from ringo.views.json import action_view_mapping as ravm
    name = clazz.__tablename__
    for action in clazz.get_item_actions():
        action_name = action.name.lower()
        #  Setup web route and views
        route_name = clazz.get_action_routename(action.name.lower())
        route_url = "%s/%s" % (name, action.url)
        log.debug("Adding WEB route: %s, %s" % (route_name, route_url))
        config.add_route(route_name, route_url,
                         factory=get_resource_factory(clazz))
        view_func = wavm.get(action_name)
        if view_func:
            if action_name == "delete":
                template = "confirm"
            else:
                template = action_name
            config.add_view(view_func,
                            route_name=route_name,
                            renderer='/default/%s.mako' % template,
                            permission=action.permission or action_name)

        #  Setup REST route and views
        action_method_mapping = {
            "list": "GET",
            "create": "POST",
            "read": "GET",
            "update": "PUT",
            "delete": "DELETE"
        }
        route_name = clazz.get_action_routename(action.name.lower(),
                                                prefix="rest")
        tmpurl = action.url.split("/")
        if len(tmpurl) > 1:
            route_url = "rest/%s/%s" % (name, tmpurl[1])
        else:
            route_url = "rest/%s" % (name)
        log.debug("Adding REST route: %s, %s" % (route_name, route_url))
        config.add_route(route_name, route_url,
                         factory=get_resource_factory(clazz))
        view_func = ravm.get(action_name)
        if view_func:
            config.add_view(view_func,
                            route_name=route_name,
                            renderer='json',
                            request_method=action_method_mapping[action_name],
                            permission=action.permission or action_name)

        # Add bundle action.
        if action.name == "List":
            from ringo.views.base import bundle_
            action_name = "Bundle"
            route_name = "%s-%s" % (name, action_name.lower())
            route_url = "%s/%s" % (name, action_name.lower())
            log.debug("Adding route: %s, %s" % (route_name, route_url))
            config.add_route(route_name, route_url,
                             factory=get_resource_factory(clazz))
            config.add_view(bundle_, route_name=route_name,
                            renderer='/default/bundle.mako',
                            permission='list')


def write_formbar_static_files():
    """Will write the formbar specific css and js files into the formbar
    directory in the static file location"""
    formbar_css = os.path.join(static_dir, 'formbar')
    for filename, content in helpers.get_formbar_css():
        filename = os.path.join(formbar_css, filename)
        head, tail = os.path.split(filename)
        if not os.path.exists(head):
            os.makedirs(head)
        with open(filename, 'wb') as f:
            f.write(content)
    formbar_js = os.path.join(static_dir, 'formbar')
    for filename, content in helpers.get_formbar_js():
        filename = os.path.join(formbar_js, filename)
        head, tail = os.path.split(filename)
        if not os.path.exists(head):
            os.makedirs(head)
        with open(filename, 'wb') as f:
            f.write(content)
    log.info('-> Formbar static files written.')
