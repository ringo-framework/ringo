import os
import logging
import pkg_resources
from ringo.resources import get_resource_factory

base_dir = pkg_resources.get_distribution("ringo").location
template_dir = os.path.join(base_dir, 'ringo', 'templates')
static_dir = os.path.join(base_dir, 'ringo', 'static')

# Directory with templates to generate views and models
modul_template_dir = os.path.join(base_dir, 'ringo', 'scripts', 'templates')

log = logging.getLogger(__name__)


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
