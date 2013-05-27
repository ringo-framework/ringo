import os
import pkg_resources
from pyramid.threadlocal import get_current_registry
from formbar.helpers import get_css



def get_ringo_version():
    return pkg_resources.get_distribution('ringo').version


def get_app_name():
    registry = get_current_registry()
    return registry.__name__


def get_app_version():
    return pkg_resources.get_distribution(get_app_name()).version


def get_app_title():
    registry = get_current_registry()
    settings = registry.settings
    return settings['app.title']


def get_action_url(request, item, action):
    """Return an URL object for the given item and action. If the item
    is an instance of object then we assume that we want to get the URL
    for the specific item. So we add the ID of the instance to the url.
    If the item is the class, then no ID is added (Create actions e.g.)

    :item: loaded instance or class of an item
    :action: string of the action
    :returns: URL instance
    """
    base_name = item.__tablename__
    route_name = "%s-%s" % (base_name, action)
    if isinstance(item, object):
        return request.route_url(route_name, id=item.id)
    return request.route_url(route_name)


def get_path_to(location):
    """Will return the full pathname the given file name with in the path. path
    is relativ to the ringo package root."""
    return os.path.join(os.path.dirname(
                        os.path.abspath(__file__)), '..', location)


def get_path_to_form_config(filename):
    """Returns the path the the given form configuration. The file name
    should be realtive to the default location for the configurations.

    :file: filename
    :returns: Absolute path to the configuration file

    """
    location = "views/forms"
    return get_path_to(os.path.join(location, filename))


def get_formbar_css():
    return get_css()
