"""Modul to get information about the application"""
import os
import pkg_resources
from pyramid.threadlocal import get_current_registry
from ringo.lib.sitetree import build_breadcrumbs, site_tree_branches


def get_ringo_version():
    return pkg_resources.get_distribution('ringo').version


def get_app_inheritance_path():
    """Returns a list of application names. The names describe the path
    to the root of the application inheritance. e.g if the current
    application is 'foo' which is based and 'bar' which is based on
    'ringo' the function will return the follwing result: ['foo', 'bar',
    'ringo'].

    The default path is [<nameofcurrentapp>, "ringo"]. The path can be
    extended by setting the app.base config variable.

    :returns: List of application name which build the inheritance path.
    """
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


def get_app_mode(request):
    """Will return a tuple of the mode configuration (if configured)

    Tuple: (mode, desc, color)

    If no mode is configured return None.

    :request: Current request
    :return: Tuple of mode configruation
    """
    settings = request.registry.settings
    mode = settings.get("app.mode")
    desc = settings.get("app.mode_desc", "").decode('utf-8')
    color_primary = settings.get("app.mode_color_primary", "#F2DEDE")
    color_secondary = settings.get("app.mode_color_secondary", "red")
    if mode:
        return (mode, desc, color_primary, color_secondary)
    return None


def get_app_title():
    """Will return the title of the application

    :return: The title of the application"""
    registry = get_current_registry()
    settings = registry.settings
    return settings['app.title']


def get_app_customstatic(url=None):
    """Will return the path of the custom static folder which can be
    used for branding. If no configured the folder is the same folder
    that ringo:static."""
    registry = get_current_registry()
    settings = registry.settings
    customstatic = settings.get('app.customstatic', 'ringo:static')
    if url:
        return "{}/{}".format(customstatic, url)
    else:
        return customstatic


def get_app_logo():
    """Will return the path of the application logo. Which should be
    displayed.

    :return: The path to the application logo"""
    registry = get_current_registry()
    settings = registry.settings
    logo = settings.get('app.logo')
    if logo:
        return get_app_customstatic(logo)
    return None


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


def get_breadcrumbs(request, strategy=None):
    """Will return a list of elements which are used to build the
    breadcrumbs in the UI.

    The function take a strategy attribute which is called to build this
    list instead of the default mechanism of ringo. The strategy
    function takes the current request as attribute

    The returned list currently must have the follwing format::

        [(label of element, url of element), (), ...]

    The last element in the list shoul be the current element and has no
    link. (URL is None)

    :request: Current request
    :strategy: Optional function which is called to build the site tree.
    :returns: List of elements used for building a the breadcrumbs.

    """
    if strategy is None:
        strategy = build_breadcrumbs
    tree = {}
    for branch in site_tree_branches:
        tree.update(branch)
    return strategy(request, tree)
