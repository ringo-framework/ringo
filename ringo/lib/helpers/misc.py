import logging
import re
import string
import base64
import sqlalchemy as sa
from datetime import datetime
from pyramid.threadlocal import get_current_request, get_current_registry
import formbar.converters as converters
from ringo.lib.sql import DBSession


log = logging.getLogger(__name__)

re_char_match = re.compile("(var){0,1}char\([0-9]+\)")


def deserialize(value, datatype):
    """Very simple helper function which returns a python version
    of the given serialized value."""
    if datatype in ["varchar", "text"]:
        return value
    elif value in ["", None]:
        return None
    elif datatype == "integer":
        return converters.to_integer(value)
    elif datatype == "float":
        return converters.to_float(value)
    elif datatype == "datetime":
        # Interval fields are implemented as DATETIME
        # See http://docs.sqlalchemy.org/en/latest/core/type_basics.html#sqlalchemy.types.Interval
        # Check if we have a interval here
        iv = re.compile(u"^\d{1,2}:\d{1,2}:\d{1,2}")
        if iv.match(value):
            t = datetime.datetime.strptime(value, "%H:%M:%S")
            return datetime.timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)

        # We need the configured timezone to convert the datetime into
        # the correct timezone.
        if get_current_registry().settings:
            timezone = get_current_registry().settings.get("app.timezone")
        else:
            timezone = None
        return converters.to_datetime(value, locale=None, timezone=timezone)
    elif datatype == "date":
        return converters.to_date(value)
    elif re_char_match.match(datatype):
        # UUID
        return value
    elif datatype == "blob":
        return base64.b64decode(value)
    elif datatype == "boolean":
        # In case of imports from a JSON file the value is already of
        # type boolean.
        if isinstance(value, bool):
            return value
        else:
            converters.to_boolean(value)
    else:
        raise TypeError("{} is not supported".format(datatype))


def serialize(value):
    """Very simple helper function which returns a stringified version
    of the given python value."""
    if value is None:
        return ""
    if isinstance(value, unicode):
        return value
    if isinstance(value, str):
        return unicode(value)
    if isinstance(value, int):
        return unicode(value)
    if isinstance(value, float):
        return unicode(value)
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
    # Even if Ringo does not have a bytearray type yet the serialize
    # method supports it to convert the given value into unicode
    if isinstance(value, bytearray):
        return value.decode("utf-8")

    log.warning("Unhandled type '%s'. "
                "Using default and converting to unicode" % type(value))
    try:
        return unicode(value)
    except UnicodeDecodeError:
        return base64.b64encode(value)


def safestring(unsafe):
    """Returns a 'safe' version of the given string. All non ascii chars
    and other chars are removed """
    valid_chars = "_%s%s" % (string.ascii_letters, string.digits)
    return ''.join(c for c in unsafe if c in valid_chars)


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


def _resolve_attribute(element, name, idx=None):
    """Helper method for the set_raw_value and get_raw_value method.
    Will return on default the last element in a dot
    separated attribute. E.g. for a attribute called 'foo.bar.baz' the
    function will return a the 'baz' element.

    The default element to return can can be changed by providing the
    idx attribute. The idx will be used to iterate over the splitted
    attribute name. ([0:idx]). This is usually only used when trying to
    set a value. See set_raw_value for more details.

    The function also offers basic support for accessing individual
    elements in lists in case one attribute is a list while iterating
    over all attributes. Currently only flat lists are supported.

    Example: x.y[1].z

    The method is tolerant agains errors when trying to resolve elements
    in lists which are not present. This is likly the case for relations
    when x has no elements stored in relation y. In this case the method
    stops resolving the value and returns None. However we log this
    situation in the debugging output as it might be a sign for an
    error.

    :element: BaseItem instance
    :name: dot separated attribute name
    :returns: last element of the dot separated element.

    """
    attributes = name.split('.')
    if idx is None:
        idx = len(attributes)
    for attr in attributes[0:idx]:
        splitmark_s = attr.find("[")
        splitmark_e = attr.find("]")
        if splitmark_s > 0:
            index = int(attr[splitmark_s + 1:splitmark_e])
            attr = attr[:splitmark_s]
            element_list = object.__getattribute__(element, attr)
            if len(element_list) > 0:
                element = element_list[index]
            else:
                log.debug("IndexError in %s on %s for %s"
                          % (name, attr, element))
                element = None
                break
        else:
            element = object.__getattribute__(element, attr)
    return element


def set_raw_value(element, name, value):
    """Support setting the `value` for a dot separated attribute of
    `element` provided by the `name` attribute. If the attribute name is
    a dot separated attribute the function will first resolve the
    attribute to the penultimate element and call the setattr method for
    the ultimate element and the given value.

    E.g. If the value '123' should be set for the attribute
    'foo.bar.baz' the function first gets the 'bar' element.  For this
    element the setattr method will be called with the attribute 'baz'
    and the value '123'."""

    if name.find(".") > -1:
        penulti = _resolve_attribute(element, name, -1)
        attr = name.split(".")[-1]
    else:
        penulti = element
        attr = name
    object.__setattr__(penulti, attr, value)


def get_raw_value(element, name):
    """Support getting the value for a dot separated attribute of
    `element` provided by the `name` attribute. If the attribute name is
    a dot separated attribute the function will first resolve the
    attribute to the penultimate element and call the getattr method for
    the ultimate element and the given value.

    E.g. If the function should get the attribute 'foo.bar.baz' the
    function first gets the 'bar' element.  For this element the getattr
    method will be called with the attribute 'baz'."""

    return _resolve_attribute(element, name)


def dynamic_import(cl):
    d = cl.rfind(".")
    classname = cl[d + 1:len(cl)]
    m = __import__(cl[0:d], globals(), locals(), [classname])
    return getattr(m, classname)


def get_modul_by_name(modulname, session=DBSession):
    # FIXME:
    # Compatibilty mode. Older versions of Ringo added a 's' to the
    # extensions modul name as Ringo usally uses the plural form.
    # Newer versions use the configured extension name. So there
    # might be a mixture of old and new modul names in the database.
    # This code will handle this. (ti) <2016-01-04 13:50>
    from ringo.model.modul import ModulItem
    return session.query(ModulItem).filter(
        sa.or_(ModulItem.name == modulname,
               ModulItem.name == modulname + 's')).scalar()


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
    modul = DBSession.query(ModulItem).get(mid)
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
        # FIXME: Ideally there is no need to call the methods without a
        # request and to get the request from the app globals. If this
        # code path is executed this is a sign the the caller is not
        # implemented in a clean way. Well, this is a known issue for
        # years and it currently doesn't seem to cause problems in the
        # real world. (ti) <2016-01-12 08:55>
        request = get_current_request()
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


def get_open_url(request, item):
    """Convinience method to the a URL to 'open' the item."""
    from ringo.lib.security import has_permission

    permissions = ['read']
    # If the application is configured to open items in readmode on
    # default then we will not add the update action to the actions to
    # check.
    if not request.registry.settings.get("app.readmode") in ["True", "true"]:
        permissions.append('update')

    url = None
    for permission in permissions:
        if has_permission(permission, item, request):
            route_name = get_action_routename(item, permission)
            url = request.route_path(route_name, id=item.id)
        else:
            break
    return url


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
        # If backurl is set
        if hasattr(request.context, "__model__"):
            clazz = request.context.__model__
            backurl = request.session.get('%s.backurl' % clazz)
        else:
            backurl = None
        query = {}
        if backurl:
            query['backurl'] = backurl
        return request.route_path(route_name, id=item.id, _query=query)
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
    # FIXME: Circular import (ti) <2015-05-11 21:52>
    from ringo.lib.security import has_permission
    user_moduls = []
    # The modules has been load already and are cached. So get them from
    # the cache
    for modul in request.cache_item_modul.all().values():
        # Only show the modul if it matches the desired display location
        # and if the modul has an "list" action which usually is used as
        # entry point into a modul.
        if (modul.display == display and modul.has_action('list')):
            clazz = dynamic_import(modul.clazzpath)
            if has_permission('list', clazz, request):
                user_moduls.append(modul)
    return user_moduls
