"""Modul to get information about the application"""
import os
import pkg_resources
from pyramid.threadlocal import get_current_registry


def get_ringo_version():
    return pkg_resources.get_distribution('ringo').version


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
    """Returns the base url of the application if configured. The base
    url can be configured using the `app.url` config variable in the ini
    file. The configuration defaults to having no explizit base url. If
    the `app.url` variable is emtpy we will determine the base url from
    request.application_url variable. Else the value of `app.url` is
    used"""
    settings = request.registry.settings
    app_url = settings.get("app.url")
    if app_url is None:
        # Default! No url.
        return ""
    elif app_url == "":
        return request.application_url
    else:
        return app_url


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
