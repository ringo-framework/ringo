"""Modul to get information about the application"""
import os
import pkg_resources
from pyramid.threadlocal import get_current_registry


def get_ringo_version():
    return pkg_resources.get_distribution('ringo').version


def get_app_inheritance_path():
    """Returns a list of application names. The names describe the path
    to the root of the application inheritance. e.g if the current
    application is 'foo' which is based and 'bar' which is based on
    'ringo' the function will return the follwing result: ['foo', 'bar',
    'ringo'].

    The default path is [<nameofcurrentapp>, "ringo"]. The path can be
    extended by setting the app.base config variable."""
    path = ['ringo']
    registry = get_current_registry()
    settings = registry.settings
    base = settings.get("app.base")
    if base:
        path.append(base)
    path.append(get_app_name())
    return reversed(path)


def get_app_name():
    registry = get_current_registry()
    return registry.__name__


def get_app_version():
    return pkg_resources.get_distribution(get_app_name()).version


def get_app_location(name=None):
    if not name:
        name = get_app_name()
    return pkg_resources.get_distribution(name).location


def get_app_url(request):
    """Returns the path of the application under which the application
    is hosted on the server.

    .. note::
        This function is a helper function. It is only used to build
        correct URLs for client sided AJAX requests in case the
        application is hosted in a subpath.

    Example:

    If the application is hosted on "http://localhost:6543/foo" the
    function will return "foo". If it is hosted under the root
    directory '' is returned."""
    return request.environ.get("SCRIPT_NAME", "")
    

def get_app_title():
    registry = get_current_registry()
    settings = registry.settings
    return settings['app.title']


def get_path_to(location, app=None):
    """Will return the full pathname the given file name with in the
    path. path is relativ to the application package (pkg_ressource
    location + ressource name). You can define a alternative
    application."""
    if app:
        app_name = app
    else:
        app_name = get_app_name()
    base_path = os.path.join(get_app_location(app_name), app_name)
    return os.path.join(base_path, location)
