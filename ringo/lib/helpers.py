import os
from datetime import datetime, timedelta
import pkg_resources
from pyramid.threadlocal import get_current_registry
from formbar.helpers import get_css, get_js


def dynamic_import(cl):
    d = cl.rfind(".")
    classname = cl[d+1:len(cl)]
    m = __import__(cl[0:d], globals(), locals(), [classname])
    return getattr(m, classname)

def import_model(clazzpath):
    """Will return the clazz defined by modul entry in the database of
    the given model. The clazzpath defines the base clazz which which
    defines the ID of the modul it belongs to.
    The function will first import the clazz and load the related modul
    entry for the model from the database. The we look for the clazzpath
    entry of the modul. If the moduls clazzpath is the same as the model
    clazzpath the return the imported model.
    If the clazzpath differs then import the model defined by the moduls
    clazzpath."""
    from ringo.lib.sql import DBSession
    from ringo.model.modul import ModulItem
    orig_clazz = dynamic_import(clazzpath)
    # Load entry from the database for the given modul
    mid = orig_clazz._modul_id
    modul = DBSession.query(ModulItem).filter_by(id=mid).one()
    if modul.clazzpath == clazzpath:
        return orig_clazz
    else:
        return import_model(modul.clazzpath)

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


def get_path_to_form_config(filename, app=None):
    """Returns the path the the given form configuration. The file name
    should be realtive to the default location for the configurations.

    :file: filename
    :returns: Absolute path to the configuration file

    """
    location = "views/forms"
    return get_path_to(os.path.join(location, filename), app)


def get_path_to_overview_config(filename, app=None):
    """Returns the path the the given overview configuration. The file name
    should be realtive to the default location for the configurations.

    :file: filename
    :returns: Absolute path to the configuration file

    """
    location = "views/tables"
    return get_path_to(os.path.join(location, filename), app)


def get_saved_searches(request, name):
    """Returns a dictionary with the saved searches for the named overview.
    :request: Current request
    :name: Name of the overview
    :returns: Dictionary with the saved seaerches.
    """
    if not request.user:
        return {}
    searches_dic = request.user.settings.get('searches', {})
    if searches_dic:
        searches_dic_search = searches_dic.get(name, {})
        return searches_dic_search
    return {}


def get_modules(request, display):
    # TODO: Fix imports here. Seems to be circular imports.
    from ringo.model.modul import ModulItem
    from ringo.resources import get_resource_factory
    from ringo.lib.security import has_permission
    listing = ModulItem.get_item_list(request.db)
    user_moduls = []
    for item in listing.items:
        # Only show the modul if it matches the desired display location
        # and if the modul has an "list" action which usually is used as
        # entry point into a modul.
        if (item.display == display and item.has_action('list')):
            # Build a ressource and to be able to check the current user
            # permissions against it.
            clazz = dynamic_import(item.clazzpath)
            factory = get_resource_factory(clazz)
            resource = factory(request)
            if has_permission('list', resource, request):
                user_moduls.append(item)
    return user_moduls

def get_formbar_css():
    return get_css()

def get_formbar_js():
    return get_js()
    return get_css()

###########################################################################
#                               Times & Dates                             #
###########################################################################

def get_week(current_datetime):
    """Returns a tuple definig the start and end datetime for the week of
    the given date. Time from 00:00:00 -> 23:59:59"""
    last_day = 6
    current_day = current_datetime.weekday()
    _ws = current_datetime - timedelta(days=(current_day))
    _we = current_datetime + timedelta(days=(last_day - current_day))
    week_start = _ws.replace(hour=0, minute=0,
                             second=0, microsecond=0)
    week_end = _we.replace(hour=23, minute=59,
                           second=59, microsecond=0)
    return (week_start, week_end)


def format_timedelta(td):
    """Returns a formtted out put of a given timedelta in the form
    00:00:00"""
    if td < timedelta(0):
        return '-' + format_timedelta(-td)
    else:
        hours = td.total_seconds() // 3600
        minutes = (td.seconds % 3600) // 60
        seconds = td.seconds % 60
    return '%02d:%02d:%02d' % (hours, minutes, seconds)
