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
