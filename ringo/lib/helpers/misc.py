import logging
from datetime import datetime
from pyramid.threadlocal import get_current_request
from ringo.lib.sql import DBSession

log = logging.getLogger(__name__)


def serialize(value):
    """Very simple helper function which returns a stringified version
    of the given python value."""
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, bool):
        # use 1 and 0 here to be able to set this values on import,
        # "True" and "False" will fail.
        return value and "1" or "0"
    # Now handle relations, 3 cases: empty, 1 item and 2+ items.
    if isinstance(value, list) and not value:
        return []
    # cannot import BaseItem here, so check for BaseItem with hasattr.
    if isinstance(value, list) and hasattr(value[0], 'id'):
        return sorted([v.id for v in value])
    if hasattr(value, 'id'):
        return [value.id]
    return unicode(value)


def age(when, on=None):
    """Returns the age in years from the given date "when" since today. If
    "on" is provided the age will be calculated relative to the given
    date. See http://keyes.ie/calculate-age-with-python/

    :when: datetime object
    :on: datetime object
    :returns: integer

    """
    if on is None:
        on = datetime.today()
    was_earlier = (on.month, on.day) < (when.month, when.day)
    return on.year - when.year - (was_earlier)


def get_raw_value(element, name):
    """This function tries to get the given attribute of the item if
    it can not be found using the usual way to get attributes. In
    this case we will split the attribute name by "." and try to get
    the attribute along the "." separated attribute name. The
    function also offers basic support for accessing individual
    elements in lists in case one attribute is a list while
    iterating over all attributes. Currently only flat lists are
    supported.

    Example: x.y[1].z"""
    attributes = name.split('.')
    for attr in attributes:
        splitmark_s = attr.find("[")
        splitmark_e = attr.find("]")
        if splitmark_s > 0:
            index = int(attr[splitmark_s + 1:splitmark_e])
            attr = attr[:splitmark_s]
            element_list = object.__getattribute__(element, attr)
            if len(element_list) > 0:
                element = element_list[index]
            else:
                log.error("IndexError in %s on %s for %s"
                          % (name, attr, self))
                element = None
                break
        else:
            element = object.__getattribute__(element, attr)
    return element


def dynamic_import(cl):
    d = cl.rfind(".")
    classname = cl[d + 1:len(cl)]
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
    from ringo.model.modul import ModulItem
    orig_clazz = dynamic_import(clazzpath)
    # Load entry from the database for the given modul
    mid = orig_clazz._modul_id
    modul = DBSession.query(ModulItem).filter_by(id=mid).one()
    if modul.clazzpath == clazzpath:
        return orig_clazz
    else:
        # TODO: Is this code ever reached? (ti) <2014-02-25 23:07>
        return import_model(modul.clazzpath)


def get_item_modul(request, item):
    if hasattr(item, "_modul_id"):
        return _get_item_modul(request, item)
    else:
        return _get_item_modul(request, item.__class__)


def _get_item_modul(request, item):
    if not request:
        request = get_current_request()
        # Log this message only once per request!
        if request and not hasattr(request, "has_logged_get_current_request_warning"):
            log.warning("Calling get_item_modul with no request although "
                        "there is a request available. "
                        "Using 'get_current_request'...")
            request.has_logged_get_current_request_warning = True
    if not request or not request.cache_item_modul.get(item._modul_id):
        from ringo.model.modul import ModulItem
        factory = ModulItem.get_item_factory()
        if item._modul_id is None:
            # FIXME: Special case when loading fixtures for extensions.
            # As the id of an extension is set dynamically on
            # application startup the id is not yet present at time of
            # fixture loading. (ti) <2015-02-17 23:00>
            modul = factory.load(item.__tablename__, field="name")
        else:
            modul = factory.load(item._modul_id)
        if request:
            if not request.cache_item_modul.get(item._modul_id):
                request.cache_item_modul.set(item._modul_id, modul)
        else:
            return modul
    return request.cache_item_modul.get(item._modul_id)


def get_item_actions(request, item):
    """Returns a list of ActionItems which are available for given item
    or class.  If you want to add custom actions to the modul please
    overwrite this method.

    :item: Instance or class in the model.
    :returns: List of ActionItems.
    """
    modul = get_item_modul(request, item)
    return modul.actions


def get_action_routename(item, action, prefix=None):
    """Returns a string for the given action which can be used to get or
    build a route. If prefix is provided the the prefix will be
    prepended to the route name.

    :item: Instance or class in the model.
    :action: Name of the action.
    :prefix: Optional prefix of the route name.
    :returns: List of ActionItems.
    """
    routename = "%s-%s" % (item.__tablename__, action)
    if prefix:
        return "%s-%s" % (prefix, routename)
    return routename


def get_action_url(request, item, action):
    """Return an URL object for the given item and action. If the item
    is an instance of object then we assume that we want to get the URL
    for the specific item. So we add the ID of the instance to the url.
    If the item is the class, then no ID is added (Create actions e.g.)

    :item: loaded instance or class of an item
    :action: string of the action
    :returns: URL instance
    """
    route_name = get_action_routename(item, action)
    if isinstance(item, object):
        return request.route_path(route_name, id=item.id)
    # TODO: Is this code ever reached. See testcase (ti) <2014-02-25 23:17>
    return request.route_path(route_name)


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
    from ringo.model.base import get_item_list
    modules = get_item_list(request, ModulItem)
    user_moduls = []
    for modul in modules.items:
        # Only show the modul if it matches the desired display location
        # and if the modul has an "list" action which usually is used as
        # entry point into a modul.
        if (modul.display == display and modul.has_action('list')):
            # Build a ressource and to be able to check the current user
            # permissions against it.
            clazz = dynamic_import(modul.clazzpath)
            factory = get_resource_factory(clazz, modul)
            resource = factory(request, modul)
            if has_permission('list', resource, request):
                user_moduls.append(modul)
    return user_moduls
