"""Items are instances of a certain type of data which is defined in a
of a :mod:`.modul`.

All items in ringo are derived at least from :class:`.BaseItem` and one ore
more mixins from the :mod:`.mixins` modul.

Further ringo provides a :class:`.BaseFactory` to create new items and a
:class:`.BaseList` to handle lists of items for all modules.
"""
import logging
import warnings
import operator
import math
import re
import uuid
from sqlalchemy import Column, CHAR
from sqlalchemy.orm import joinedload, Session
from ringo.lib.helpers import serialize, get_item_modul, get_raw_value
from ringo.lib.cache import CACHE_MODULES
from ringo.lib.form import get_form_config
from ringo.lib.table import get_table_config
from ringo.lib.sql import DBSession
from ringo.lib.sql.cache import regions
from ringo.lib.sql.query import FromCache, set_relation_caching
from ringo.lib.alchemy import get_columns_from_instance
from ringo.model.mixins import StateMixin, Owned

log = logging.getLogger(__name__)

opmapping = {
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
    "!=": operator.ne,
    "==": operator.eq
}


def nonecmp(a, b):
    if a is None and b is None:
        return 0
    if a is None:
        return -1
    if b is None:
        return 1
    return cmp(a, b)


def attrgetter(field, expand):
    def g(obj):
        return resolve_attr(obj, field, expand)
    return g


def resolve_attr(obj, attr, expand):
    return obj.get_value(attr, expand=expand)


def load_modul(item):
    """Will load the related modul for the given item. First we try to
    get the bound session from the object and reuse this session to load
    the modul item. If the item has no bound session then call the
    get_item_modul method with no request.

    :item: item
    :returns: modul instance

    """
    from ringo.model.modul import ModulItem
    session = Session.object_session(item)
    mid = item.__class__._modul_id
    # Loading the modul is expensive! So try to cache it.
    if not CACHE_MODULES.get(mid):
        if session:
            modul = session.query(ModulItem).filter_by(id=mid).one()
        else:
            modul = get_item_modul(None, item)
        CACHE_MODULES.set(modul.id, modul)
    return CACHE_MODULES.get(mid)


class BaseItem(object):

    _modul_id = None
    _sql_eager_loads = []
    """Configure a list of relations which are configured to be
    eager loaded."""

    # Added UUID column for every BaseItem. This is needed to identify
    # item on imports and exports.
    uuid = Column('uuid', CHAR(32),
                  unique=True,
                  nullable=False,
                  default=lambda x: '%.32x' % uuid.uuid4())

    def render(self):
        """This function can be used to render a different
        representation of the item. On default it also returns the
        simple string representation. Usefull to build some HTML used in
        links e.g overviews and lists"""
        return self.__str__()

    def __str__(self):
        return self.__unicode__()

    def __cmp__(self, other):
        """Comparision of the elements are done on their string
        representation"""
        s = unicode(self)
        o = unicode(other)
        if s < o:
            return -1
        elif s == o:
            return 0
        else:
            return 1

    def __getitem__(self, name):
        return self.get_value(name)

    def __getattr__(self, name):
        return get_raw_value(self, name)

    def __unicode__(self):
        """Will return the string representation for the item based on a
        configured format string in the modul settings. If no format str
        can be found return the id of the item.

        The format string must have the following syntax:
        format_str|field1,field2,....fieldN. where format_str in a
        string with %s placeholders and fields is a comma separated list
        of fields of the item"""
        modul = load_modul(self)
        format_str, fields = modul.get_str_repr()
        if format_str:
            return format_str % tuple([self.get_value(f) for f in fields])
        else:
            return "%s" % str(self.id or self.__class__)

    @classmethod
    def get_item_factory(cls):
        return BaseFactory(cls)

    def reset_uuid(self):
        self.uuid = '%.32x' % uuid.uuid4()

    def get_value(self, name, form_id="read", expand=False):
        """Return the value of the given attribe of the item. Unlike
        accessing the raw value through the attribite directly this
        function will apply all configured transformations to the value
        before returing it."""
        try:
            raw_value = getattr(self, name)
        except:
            # This error is only acceptable for blobforms as attributes
            # can be added and removed by the user on the fly. So there
            # is a good chance that older items do not have this attribute.
            if hasattr(self, 'id'):
                log.error("Attribute '%s' not found in '%s'; id:%s"
                          % (name, repr(self), self.id))
            else:
                log.error("Attribute '%s' not found in '%s'"
                          % (name, repr(self)))
            raw_value = None
        if expand:
            # In case the fieldname is dotted and refers to values in
            # related items then we need some special logic.
            elements = name.split(".")
            if len(elements) == 2:
                obj = getattr(self, elements[0])
                name = elements[1]
            elif len(elements) > 2:
                obj = getattr(self, ".".join(elements[0:-1]))
                name = elements[-1]
            else:
                obj = self

            form_config = get_form_config(obj, form_id)
            try:
                field_config = form_config.get_field(name)
                for option in field_config.options:
                    if str(raw_value) == str(option[1]):
                        return option[0]
            except KeyError:
                log.error("Field %s not found in form config" % name)
        return raw_value

    def get_values(self, include_relations=False, serialized=False):
        """Will return a dictionary with the values of the item. If
        include_relations is true, than the realtion values are
        included. Else only scalar values are included"""
        values = {}
        for field in get_columns_from_instance(self, include_relations):
            # Ignore private form fields
            if field.startswith("_"):
                continue
            if serialized:
                value = serialize(getattr(self, field))
            else:
                value = getattr(self, field)
            values[field] = value
        return values

    def set_values(self, values):
        """Will set the values of the items attributes to the given
        values in the dictionary. Attributes beginning with "_" are
        considred private and are ignored.

        This function will not handle saving the changed data. This can
        be by either calling the save method of the item, or
        automatically at the transactions end if autocommit is enabled.

        Please note that setting the values for foreign key attributes
        might not work as expected. This is especially true for foreign
        keys to already existing items. You are not able to change a
        existing relation in the items by changing the foreign key value
        (You must do this by setting the related item). In this case the
        value for the foreign key seems to be ignored and replaced by
        the one of the actual related item.
        In contrast you can set a new relation by setting the foreign
        key if this is a new relation.

        :values: Dictionary with values to be set
        """

        for key, value in values.iteritems():
            # Ignore private form fields
            if key.startswith('_'):
                continue
            if hasattr(self, key):
                log.debug("Setting value '%s' in %s" % (value, key))
                setattr(self, key, value)
            else:
                log.warning('Not saving "%s". Attribute not found' % key)

    def save(self, data, request=None):
        """Will save the given data into the item. If the current item
        has no value for the id attribute it is assumed that this item
        must be added to the database as a new item. In this case you
        need to provide a dbsession as the new item is not linked to any
        dbsession yet.

        Please note, that you must ensure that the submitted values are
        validated. This function does no validation on the submitted
        data.

        :data: Dictionary with key value pairs.
        :request: Current request session. Used when saving new items.
        :returns: item with new data.

        """
        if request:
            dbsession = request.db
        else:
            dbsession = None
        # Use repr here a the __unicode__ method default to self.id
        # which might not be available here
        log.debug("Saving %s" % repr(self))

        old_values = self.get_values()
        # Set values
        self.set_values(data)

        # Handle statechange
        if isinstance(self, StateMixin):
            for key in self.list_statemachines():
                new_state_id = data.get(key)
                old_state_id = old_values.get(key)
                if ((new_state_id and old_state_id)
                   and (new_state_id != old_state_id)):
                    self.change_state(request, key,
                                      old_state_id, new_state_id)

        #  FIXME: Fix building a log entry. The log modul has been
        #  converted to an extension and is not available in the ringo
        #  core (ti) <2015-01-31 19:04>
        ## Handle logentry
        #if isinstance(self, Logged):
        #    if not self.id:
        #        subject = "Create"
        #        text = json.dumps(self.build_changes(old_values, data))
        #    else:
        #        subject = "Update"
        #        text = json.dumps(self.build_changes(old_values, data))
        #    self.add_log_entry(subject, text, request)

        # If the item has no id, then we assume it is a new item. So
        # add it to the database session.
        if not self.id and dbsession:
            dbsession.add(self)
            # flush the session to make the new id in the element
            # presistent.
            dbsession.flush()

            # Check if uid or gid or uid inheritance is configured.
            if isinstance(self, Owned):
                gid_relation = getattr(self, '_inherit_gid')
                if gid_relation:
                    parent = getattr(self, gid_relation)
                    # FIXME: Check why this attribute can be None. (ti)
                    # <2014-04-01 13:37>
                    if parent:
                        self.group = parent.group
                    else:
                        log.warning("Inheritance of group '%s' failed. "
                                    "Was None" % gid_relation)
                uid_relation = getattr(self, '_inherit_uid')
                if uid_relation:
                    parent = getattr(self, uid_relation)
                    if parent:
                        self.owner = parent.owner
                    else:
                        log.warning("Inheritance of group '%s' failed. "
                                    "Was None" % gid_relation)
        return self

########################################################################
#                               BaseList                               #
########################################################################


def get_item_list(request, clazz, user=None, cache="", items=None):
    """Returns a BaseLists instance with items of the given clazz. You
    can optionally provide a user object. If provided the list will only
    contain items which are readable by user in the current request.
    Further you can define a caching region to cache the results of the
    sqlquery. If not provided no caching is done.

    :request: Current request
    :clazz: Clazz for with the items in the baselist will be loaded.
    :user: If provided only items readable for the
           user in the current request are included in the list
    :cache: Name of the cache region. If empty then no caching is
            done.
    :items: Set items of the Baselist. If provided no items will be
    loaded.
    :returns: BaseList instance

    """
    key = "%s-%s" % (clazz._modul_id, user)
    if not request.cache_item_list.get(key):
        listing = BaseList(clazz, request.db, cache, items)
        if user:
            listing = filter_itemlist_for_user(request, listing)
        # Only cache the result if not items has been prefined for the
        # list.
        if items is None:
            request.cache_item_list.set(key, listing)
        else:
            return listing
    return request.cache_item_list.get(key)


def filter_itemlist_for_user(request, baselist):
    """Returns a filterd baselist. The items are filterd based on
    the permission of the current user in the request. Only items are
    included where the given user has read access. This means:

     1. The user has aproriate role (read access)
     2. Is owner or member of the items group

    :request: Current request
    :baselist: BaseList instance
    :returns: Filtered BaseList instance

    """
    from ringo.lib.security import has_permission
    filtered_items = []
    if request.user and not request.user.has_role("admin"):
        # Iterate over all items and check if the user has generally
        # access to the item.
        for item in baselist.items:
            # Only check ownership if the item provides a uid.
            if has_permission('read', item, request):
                filtered_items.append(item)
        baselist.items = filtered_items
    return baselist


class BaseList(object):
    def __init__(self, clazz, db, cache="", items=None):
        """A List object of. A list can be filterd, and sorted.

        :clazz: Class of items which will be loaded.
        :db: DB connection used to load the items.
        :cache: Name of the cache region. If empty then no caching is
                done.
        :items: Set items of the Baselist. If provided no items will be
        loaded.
        """
        self.clazz = clazz
        self.db = db
        # TODO: Check which is the best loading strategy here for large
        # collections. Tests with 100k datasets rendering only 100 shows
        # that the usual lazyload method seems to be the fastest which is
        # not what if have been expected.
        #self.items = db.query(clazz).options(joinedload('*')).all()

        if items is None:
            q = self.db.query(self.clazz)
            if cache in regions.keys():
                q = set_relation_caching(q, self.clazz, cache)
                q = q.options(FromCache(cache))
            for relation in self.clazz._sql_eager_loads:
                q = q.options(joinedload(relation))
            self.items = q.all()
        else:
            self.items = items
        self.search_filter = []

    def __iter__(self):
        return iter(self.items)

    def sort(self, field, order, expand=False):
        """Will return a sorted item list. Sorting is done based on the
        string version of the value in the sort field.

        :field: Name of the field on which the sort will be done
        :order: If "desc" then the order will be reverted.
        :expand: If True, then the sorting will be done on the expanded values.
        :returns: Sorted item list

        """
        sorted_items = sorted(self.items,
                              cmp=nonecmp,
                              key=attrgetter(field, expand))
        if order == "desc":
            sorted_items.reverse()
        self.items = sorted_items

    def paginate(self, page=0, size=None):
        """This function will set some internal values for the
        pagination function based on the given params.

        :page: Integer of the current page
        :size: Items per page
        :returns:

        """
        self.pagination_size = size
        """Number of items per page"""
        self.pagination_current = page
        """Current selected page"""
        self.pagination_pages = None
        """Number of total pages in the pagination"""
        self.pagination_first = None
        """First page in pagination navigation"""
        self.pagination_last = None
        """Last page in pagination navigation"""
        self.pagination_start = None
        """Start index for slicing the items list on the current page"""
        self.pagination_end = None
        """End index for slicing the items list on the current page"""

        # Calulate the slicing indexes for paginating and the total
        # number of pages.
        if size is None:
            pages = 1
            self.pagination_start = 0
            self.pagination_end = len(self.items)
        else:
            pages = int(math.ceil(float(len(self.items)) / size))
            self.pagination_start = page * size
            self.pagination_end = (page + 1) * size
        self.pagination_pages = pages

        ## Calculate the range to the pagination navigation
        start = self.pagination_current - 4
        end = self.pagination_current + 5
        if start < 0:
            end += abs(start)
            start = 0
        elif end > self.pagination_pages:
            end = self.pagination_pages
            start -= (abs((self.pagination_pages + 5) - end))
        self.pagination_first = start
        self.pagination_last = end

    def filter(self, filter_stack):
        """This function will filter the list of items by only leaving
        those items in the list which match all search criterias in the
        filter stack. The list will get reduced with every iteration on
        the filter stack.

        For each filter in the stack the function will first look for an
        optional operator which must be the first word of the search
        expression. If a operator can be found the search will be done
        with the given operator. Otherwise the search word will be
        compiled to the regular expression.

        Then all items are iterated. For each item the function will try
        to match the value of either all, or from the configued search
        field with the regular expression or configured operator. If the
        value matches, then the item is kept in the list.
        """
        self.search_filter = filter_stack
        log.debug('Length filterstack: %s' % len(filter_stack))
        table_config = get_table_config(self.clazz)
        table_columns = {}

        # Save cols in the tableconfig for later access while getting values.
        for col in table_config.get_columns():
            table_columns[col.get('name')] = col

        for search, search_field, regexpr in filter_stack:
            search_op = None
            # Get soperator
            x = search.split(" ")
            if x[0] in ["<", "<=", ">", ">=", "!="]:
                search_op = x[0]
                search = " ".join(x[1:])
            # Build a regular expression
            if regexpr:
                re_expr = re.compile(search, re.IGNORECASE)
            else:
                re_expr = re.compile(re.escape(search), re.IGNORECASE)
            filtered_items = []
            log.debug('Filtering "%s" in "%s" with operator "%s" on %s items'
                      % (search, search_field, search_op, len(self.items)))
            if search_field != "":
                fields = [search_field]
            else:
                fields = table_columns.keys()
            for item in self.items:
                for field in fields:
                    expand = table_columns[field].get('expand')
                    value = item.get_value(field, expand=expand)
                    if isinstance(value, list):
                        value = ", ".join([unicode(x) for x in value])
                    else:
                        value = unicode(value)
                    if search_op:
                        if opmapping[search_op](value, search):
                            filtered_items.append(item)
                            break
                    else:
                        if re_expr.search(value):
                            filtered_items.append(item)
                            break
            self.items = filtered_items


class BaseFactory(object):

    def __init__(self, clazz):
        """Factory to create of load instances of the clazz.

        :clazz: The clazz of which new items will be created

        """
        self._clazz = clazz

    def create(self, user, values):
        """Will create a new instance of clazz. The instance is it is not saved
        persistent at this moment. The method will also take care of
        setting the correct ownership.

        :user: User instance will own the new created item
        :values: Optional provide a dictionary with values for the new item
        :returns: Instance of clazz

        """
        if not isinstance(values, dict):
            raise ValueError("Values must be a dictionary")
        item = self._clazz()
        # Try to set the ownership of the entry if the item provides the
        # fields.
        if (hasattr(item, 'uid')
           and user is not None):
            item.uid = user.id
        if (hasattr(item, 'gid')):
            if (user is not None and user.gid):
                item.gid = user.gid
            else:
                modul = get_item_modul(None, item)
                default_gid = modul.gid
                item.gid = default_gid
        if values:
            item.set_values(values)
        return item

    def load(self, id, db=None, cache="", uuid=False, field=None):
        """Loads the item with id from the database and returns it.

        :id: ID of the item to be loaded
        :db: DB session to load the item
        :cache: Name of the cache region. If empty then no caching is
                done.
        :uuid: If true the given id is a uuid. Default to false
        :field: If given the item can be loaded by an alternative field.
                Default to None
        :returns: Instance of clazz

        """
        if db is None:
            db = DBSession
        q = db.query(self._clazz)
        if cache in regions.keys():
            q = set_relation_caching(q, self._clazz, cache)
            q = q.options(FromCache(cache))
        for relation in self._clazz._sql_eager_loads:
            q = q.options(joinedload(relation))
        if field:
            return q.filter(getattr(self._clazz, field) == id).one()
        if uuid:
            warnings.warn("Use of 'uuid' is deprecated in load function "
                          "and will be removed in the future. Use "
                          "field='uuid' instead", DeprecationWarning)
            return q.filter(self._clazz.uuid == id).one()
        else:
            return q.filter(self._clazz.id == id).one()
