"""The term `Item` refers to an instance of a certain type of data which
is defined in of a :mod:`.modul`.  All items in Ringo are derived at
least from :class:`.BaseItem` and one ore more mixins from the
:mod:`.mixins` modul.

Ringo provides three classes to work with items in general.
:class:`.BaseList` is a class for handling listings of items. New items
are created by using a :class:`.BaseFactory`.
"""
import logging
import warnings
import operator
import math
import re
import uuid
import fuzzy
import Levenshtein
from sqlalchemy import Column, CHAR
from sqlalchemy.orm import joinedload, Session
from ringo.lib.helpers import (
    serialize, get_item_modul,
    get_raw_value, set_raw_value,
    prettify
)
from ringo.lib.cache import CACHE_MODULES
from ringo.lib.form import get_form_config
from ringo.lib.table import get_table_config
from ringo.lib.sql import DBSession
from ringo.lib.sql.cache import regions
from ringo.lib.sql.query import FromCache, set_relation_caching
from ringo.lib.alchemy import get_columns_from_instance
from ringo.model import Base
from ringo.model.mixins import StateMixin, Owned

log = logging.getLogger(__name__)


def levenshteinmatch(value, search, t):
    """Compares two strings with Levenshtein Algorithm and given
    threshold for similarity. It is a string metric for measuring the
    difference between two words, the minimum number of single-character
    edits. A threshold (between 0 and 1) can be applied for determining
    the maximum allowed single-character edits based on the word length
    of the longer word, potential floats are rounded up at this point."""
    lenV = len(value)
    lenS = len(search)

    if lenS >= lenV:
        l = math.ceil(lenS * t)
    else:
        l = math.ceil(lenV * t)
    ld = Levenshtein.distance(value.encode("utf-8"), search.encode("utf-8"))
    return ld <= l


def doublemetaphone(value, search):
    """Compares two strings by applying the Double Metaphone phonetic
    encoding algorithm of the Fuzzy library using primary and secondary
    code of a string for matching."""
    dmeta = fuzzy.DMetaphone()
    dmeta_value = dmeta(value.encode("utf-8"))
    dmeta_search = dmeta(search.encode("utf-8"))

    if value == search:
        return True

    if dmeta_value[1] is not None and dmeta_search[1] is not None:
        for v in dmeta_value:
            for s in dmeta_search:
                if v == s:
                    return True
    return dmeta_value == dmeta_search


def smatch(value, search):
    """Compares two strings by applying the Double Metaphone phonetic
    encoding algorithm and levenshteinmatch as second indicator in
    doubts.     """
    value = value.lower()
    search = search.lower()

    if value == search:
        return True

    if doublemetaphone(value, search):
        return True
    else:
        return levenshteinmatch(search, value, 0.3)


opmapping = {
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
    "!=": operator.ne,
    "==": operator.eq,
    "~": smatch
}


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
    """Base class for all items in Ringo. The class provides
    methods to get and set values of the instances.

    The class overwrites the `__getattr__` and `__setattr__` methods to
    support getting and setting dot separatedattributes like
    'getattr(foo.bar.baz)'
    """

    _modul_id = None
    # TODO: Check if its possible to set the modul of the class
    # dynamically on application initialisation. This might help to get
    # rid of the annoying loading of the modul for a class (ti)
    # <2015-03-10 22:53>
    # __modul__ = None
    _sql_eager_loads = []
    """Configure a list of relations which are configured to be
    eager loaded."""

    uuid = Column('uuid', CHAR(36),
                  unique=True,
                  default=lambda x: str(uuid.uuid4()))

    def render(self, request=None):
        """This function can be used to render a different
        representation of the item. On default it also returns the
        simple string representation. Usefull to build some HTML used in
        links e.g overviews and lists"""
        return self.__unicode__()

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
        # In some cases it is needed to be able to trigger getting the
        # exapanded value without calling the get_value method. This can
        # be achieved by accessing the attribute with a special name.
        # Lets say you want to get the expanded value for `foo`. You get
        # this by asking for `foo__e_x_p_a_n_d`
        if name.endswith("__e_x_p_a_n_d"):
            return self.get_value(name.replace("__e_x_p_a_n_d", ""),
                                  expand=True)
        return get_raw_value(self, name)

    def __setattr__(self, name, value):
        return set_raw_value(self, name, value)

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
            return format_str % tuple([prettify(None, self.get_value(f)) for f in fields])
        else:
            return "%s" % str(self.id or self.__class__)

    @classmethod
    def get_item_factory(cls, request=None):
        """Will return the :class:`.BaseFactory` for this class. Use
        this function to create and return specific factories for the
        class."""
        return BaseFactory(cls, request)

    @classmethod
    def get_item_list(cls, request=None, user=None, cache="", items=None):
        return get_item_list(request, cls, user, cache=cache, items=items)

    @classmethod
    def _get_permissions(cls, modul, item, request):
        """Internal method to implement getting specific build of an ACL
        for this class (and instances). By default this function just
        calls the :func:`ringo.lib.security.get_permission` function.
        See this function for more details.

        If you need to implement an alternative permission check this
        function can be overwritten.  The `modul` and `item` attribute
        needed for the default get_permission method. `request` is used
        to get the current db session in case you need to reload other
        informations.

        :modul: Instance of the modul
        :item: Instance of the class
        :returns: List of permissions.

        """
        # FIXME: Try to get rid of the request element here. There
        # should not be any request needed in the model. This is needed
        # in the efa application for Participants to load additional
        # modules. (ti).
        # <2015-03-10 22:46>

        # FIXME: Circular import :((( Yes I know. We really need some
        # clean up here. (ti) <2015-03-10 21:08>
        from ringo.lib.security import get_permissions
        return get_permissions(modul, item)

    def reset_uuid(self):
        self.uuid = str(uuid.uuid4())

    def get_value(self, name, form_id="read", expand=False, strict=True):
        """Return the value of the given attribute of the item. Unlike
        accessing the value directly this function this function
        optionally supports the expansion of the value before
        returning it. On default no expansion is done.

        Expansion is relevant for values which are saved as integer
        values in the database but have another literal meaning. This is
        typically true for values in selection lists. E.g the literal
        values for 'Yes' and 'No' are saves as value '1' and '0' in the
        database. To expand the value the method will try to get the
        literal value from the value in the database by looking in the
        form identified by the `form_id` attribute.

        Strict mode means that in case the given attribute `name` can
        not be accesses a error log message will be triggered. However
        there are some cases where the attribute can not be accesses for
        some known reasons and therefor the error should not be logged
        but passed silently. As this is highly situation depended you
        can call this method with `stric=False` to prevent logging. Here
        are two examples where you migh want to disable logging:

            * Overviews. In case you want to display related items like
            'country.code' but the item does not have a related country (yet).
            * For blobforms as attributes can be added and removed by
            the user on the fly. So there is a good chance that older
            items do not have this attribute.

        :name: Name of the attribute with the value
        :form_id: ID of the form which will be used for expansion
        :expand: Expand the value before returning it
        :strict: Log error if the value can not be accessed. Defaults to True.
        :returns: Value of the named attribute
        """

        try:
            raw_value = getattr(self, name)
        except AttributeError:
            if not strict:
                pass
            elif hasattr(self, 'id'):
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

            # Expanding the value means to get the "literal" value for the
            # given value from the form.
            form_config = get_form_config(obj, form_id)
            try:
                field_config = form_config.get_field(name)
                options = []
                for option in field_config.options:
                    # Handle "list" values "{"",1,2}"
                    if str(raw_value).startswith("{") and str(raw_value).endswith("}"):
                        for value in raw_value.strip("}").strip("{").split(","):
                            if str(value) == str(option[1]):
                                options.append(option[0])
                    elif str(raw_value) == str(option[1]):
                        options.append(option[0])
                        break
                # If we can not match a value we return the raw value.
                # This can also happen if the user tries to expand value
                # which do not have options.
                if len(options) > 0:
                    return ", ".join(options)
                return raw_value
            except KeyError:
                # If the field/value which should to be expanded is not
                # included in the form the form library will raise a
                # KeyError exception. However this is not a big deal as
                # we still have the raw value and only the expandation
                # fails. So silently ignore this one. The exception is
                # already logged in the form library.
                pass
        return raw_value

    def get_values(self, include_relations=False, serialized=False):
        """Will return a dictionary with the values of the item. On
        default the function will return the pythonic values and
        excludes all related items. This behaviour can be changed by
        setting the `include_relations` and `serialized` option.

        In case the relations are included and the values are serialized
        then the serialized value of a related item is its id.

        :include_relations: Flag if relations should be included in the
                            returned dictionary.
        :serialized: Flag if the values should be serialized.
        :returns: Dictionary with key value pairs.
        """
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

    def set_values(self, values, use_strict=False):
        """Will set the values of the item. The values to be set are
        provided by a dictionary with key value pairs given with the
        `values` option. Keys in the dictionary beginning with "_" are
        considered private and are ignored.

        This function does not explicit handle saving the changed data!
        Saving data (E.g making a new instance of an item persistent in
        the DB) is handled by the :func:`.BaseItkkem.save` method.

        .. note::
            Setting the values for foreign key attributes might not work
            as expected. This is especially true for foreign keys to
            already existing items. You are not able to change a
            existing relation in the items by changing the foreign key
            value (You must do this by setting the related item). In
            this case the value for the foreign key seems to be ignored
            and replaced by the one of the actual related item.  In
            contrast you can set a new relation by setting the foreign
            key if this is a new relation.

        :values: Dictionary with values to be set
        :use_strict: boolean, if true raise a exception if an attribute is
                     missing (default: False).
        """

        for key, value in values.iteritems():
            # Ignore private form fields
            if key.startswith('_'):
                continue
            try:
                oldvalue = getattr(self, key)
                # If oldvalue is equal to the new value we need no
                # change at all in the model so continue
                if oldvalue == value:
                    continue
                log.debug(u"Setting value '%s' in %s" % (repr(value), key))
                if isinstance(value, list) and isinstance(oldvalue, list):
                    # Special handling for relations in NM relations.
                    # See ticket #19 in Ringo issue tracker for more
                    # details. Simply exchaning the relations in this
                    # case seems not to work. I case of the error in
                    # triggering the deleting of items in the
                    # nm-relation from both sides. In this case the
                    # second deletion will fail.
                    #
                    # Regarding to
                    # http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html#deleting-rows-from-the-many-to-many-table
                    # relations should be removed by using remove(item).
                    # Howver poping the items before adding the new
                    # items seems to work too. I excpet that poping the
                    # items will somehow tweak SQLAlchemy in the way
                    # that it handles deleting items correct now.
                    while oldvalue:
                        oldvalue.pop(0)
                    for nvalue in value:
                        oldvalue.append(nvalue)
                else:
                    setattr(self, key, value)
            except AttributeError:
                log.warning('Not saving "%s". Attribute/Property not found' % key)
                if use_strict:
                    raise AttributeError(('Not setting "%s".'
                                         ' Attribute not found.') % key)

    def save(self, data, request=None):
        """Method to set new values and 'saving' changes to the item. In
        contrast to just setting the values saving means triggering
        additional actions like handling state changes.

        The function will call the :func:`.BaseItem.set_values` function
        to set the values so setting the values in a separate call of
        this method is not needed. Actually doing this can cause
        problems as this function can not determine changes between old
        and new values properly anymore.

        If the current item has no value for the id attribute it is
        assumed that this item must be added to the database as a new
        item. In this case you need to provide a dbsession (as part of
        the request) as the new item is not linked to any dbsession yet.

        .. note::
            Making the changes persistent to the database is finally
            done on the end of the request when the transaction of the
            current session is commited.

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
                if ((new_state_id and old_state_id) and
                   (new_state_id != old_state_id)):
                    self.change_state(request, key, old_state_id, new_state_id)

        # FIXME: Fix building a log entry. The log modul has been
        # converted to an extension and is not available in the ringo
        # core (ti) <2015-01-31 19:04>
        # if isinstance(self, Logged):
        #     if not self.id:
        #         subject = "Create"
        #         text = json.dumps(self.build_changes(old_values, data))
        #     else:
        #         subject = "Update"
        #         text = json.dumps(self.build_changes(old_values, data))
        #     self.add_log_entry(subject, text, request)

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
    """Returns a :class:`.BaseList` instance with items of the given
    clazz. You can optionally provide a user object. If provided the
    list will only contain items which are readable by user in the
    current request.  Further you can define a caching region to cache
    the results of the sqlquery. If not provided no caching is done.

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
    if user:
        user_key = user.id
    else:
        user_key = None
    key = "%s-%s" % (clazz._modul_id, user_key)
    if not request.cache_item_list.get(key):
        listing = BaseList(clazz, request.db, cache, items)
        if user:
            listing = filter_itemlist_for_user(request, listing)
        if items is None:
            request.cache_item_list.set(key, listing)
            return listing
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
        # Mark this listing to be prefilterd for a user.
        baselist._user = request.user
    return baselist


class BaseList(object):
    """Base class for listing of items in Ringo. The class provides
    methods for sorting and filtering the items of the list.

    The BaseList is usually created by calling the
    :func:`.get_item_list` method. Using this method the BaseList will
    include all items of a given class which are readable by the current
    user.

    Alternatively the BaseList can be initiated directly in two ways. On
    default all items of a given class will be loaded from the database.
    The other way is to initiate the list with a list of preloaded
    items.
    """
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
        if items is None:
            q = self.db.query(self.clazz)

            if cache in regions.keys():
                q = set_relation_caching(q, self.clazz, cache)
                q = q.options(FromCache(cache))

            # Added support for eager loading of items in the overview:
            # http://docs.sqlalchemy.org/en/latest/orm/loading_relationships.html#relationship-loading-techniques
            # This also support loading along paths to support
            # releations which are deeper than one level.
            for relation in self.clazz._sql_eager_loads:
                joinedload_path = None
                # Load along path
                for rel in relation.split("."):
                    if joinedload_path is None:
                        joinedload_path = joinedload(rel)
                    else:
                        joinedload_path = joinedload_path.joinedload(rel)
                q = q.options(joinedload_path)
            self.items = q.all()
        else:
            self.items = items
        self.search_filter = []

        self._user = None
        """Internal variable which is set by the `filter_itemlist_for_user`
        method to indicate that the list has been build for this user
        and only contains items which are at least readable by the user.
        """

    def __iter__(self):
        return iter(self.items)

    def is_prefiltered_for_user(self):
        return self._user is not None

    def sort(self, field, order, expand=False):
        """Will return a sorted item list. Sorting is done based on the
        string version of the value in the sort field.

        :field: Name of the field on which the sort will be done
        :order: If "desc" then the order will be reverted.
        :expand: If True, then the sorting will be done on the expanded values.
        :returns: Sorted item list

        """
        def attrgetter(field, expand):
            def g(obj):
                value = obj.get_value(field, expand=expand)
                # As long as we have a model instance we will do the
                # comparison on the string representation.
                if isinstance(value, Base):
                    return unicode(value)
                return value
            return g

        def nonecmp(a, b):
            if a is None and b is None:
                return 0
            if a is None:
                return -1
            if b is None:
                return 1
            return cmp(a, b)

        sorted_items = sorted(self.items,
                              cmp=nonecmp,
                              key=attrgetter(field, expand))
        if order == "desc":
            sorted_items.reverse()
        self.items = sorted_items

    def paginate(self, total=None, page=0, size=None):
        """This function will set some internal values for the
        pagination function based on the given params.

        :total: Number of items in the list. Can be usually determined
        from the list directly.
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

        if total is None:
            total = len(self.items)

        # Calulate the slicing indexes for paginating and the total
        # number of pages.
        if size is None:
            pages = 1
            self.pagination_start = 0
            self.pagination_end = total
        else:
            pages = int(math.ceil(float(total) / size))
            self.pagination_start = page * size
            self.pagination_end = (page + 1) * size
        self.pagination_pages = pages

        # Calculate the range to the pagination navigation
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

        # If the total is equal to the count of items in the listing
        # then the list is not pageinated and the listing still includes
        # all items. In this case we will reduce the list of items to a
        # actual relevant paginated items. Otherwise it is
        # assumend that the reducing has been done done before.
        if total == len(self.items):
            self.items = self.items[self.pagination_start:self.pagination_end]

    def filter(self, filter_stack, request=None, table="overview"):
        """This function will filter the items by only leaving
        those items in the list which match all search criteria in the
        filter stack. The number of items will get reduced with every
        iteration on the filter stack. The search is case sensitive.

        The filter stack is a list of tuples which describe the filter
        expression. Each tuple consists of three values:

        1. The search expression
        2. Optionally the name of the column on which the search will be
           applied.
        3. Boolean flag to indicate that the given search expression
           should be handled as a regular expression.

        The search support three modes. On default the search will look
        for the presence of the given search string within the values of
        the item. It will also match on parts of the string. So
        searching for 'Foo' will also match 'Foobar'. Another mode is
        using the search expression as a regular expression. The last
        mode makes use of special operators. The search supports the
        following operators: "<", "<=", "!=", ">" ">=" and "~" The
        operator can be provided with the search string.  It mus be the
        first word of the search expression. If a operator is present it
        will be used.

        The "~" operator will trigger a fuzzy search using the Double
        Metaphone algorithm for determining equal phonetics. If the
        phonetics do not match the Levenshtein distance will be
        calculated.

        The search will iterate over all items in the list. For each
        item the function will try to match the value of either all, or
        from the configured search field with the regular expression or
        configured operator. If the value matches, then the item is kept
        in the list.

        :filter_stack: Filter stack
        :request: Current request.
        :table: Name of the table config which is used for the search defaults to "overview".
        :returns: Filtered list of items
        """
        self.search_filter = filter_stack
        log.debug('Length filterstack: %s' % len(filter_stack))
        table_config = get_table_config(self.clazz, table)
        table_columns = {}

        # Save cols in the tableconfig for later access while getting values.
        for col in [col for col in table_config.get_columns() if col.get("searchable", True)]:
            table_columns[col.get('name')] = col

        for search, search_field, regexpr in filter_stack:
            search_op = None
            # Get soperator
            x = search.split(" ")
            if x[0] in opmapping:
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
                    if hasattr(value, 'render'):
                        pretty_value = value.render(request)
                    elif isinstance(value, list):
                        if request and expand:
                            value = ", ".join([request.translate(unicode(x)) for x in value])
                        else:
                            value = ", ".join([unicode(x) for x in value])
                        pretty_value = value
                    else:
                        pretty_value = unicode(prettify(request, value))
                        if request and expand:
                            pretty_value = request.translate(pretty_value)
                    if search_op:
                        if request:
                            value = request.translate(unicode(value))
                        else:
                            value = unicode(value)
                        if opmapping[search_op](value, search):
                            filtered_items.append(item)
                            break
                    else:
                        if re_expr.search(pretty_value):
                            filtered_items.append(item)
                            break
            self.items = filtered_items


class BaseFactory(object):
    """Factory class to create new instances of :class:`.BaseItem` or
    derived classes. Usually the factory for items of a certain module
    can be initiated by calling the :func:`.BaseItem.get_item_factory`
    class method."""

    def __init__(self, clazz, request=None, use_strict=False):
        """Inits the factory.

        :clazz: The clazz of which new items will be created

        """
        self._clazz = clazz
        self._request = request
        self._use_strict = use_strict

    def create(self, user, values):
        """Will create a new instance of clazz. The instance is it is
        not saved persistent at this moment. The method will also take
        care of setting the correct ownership.

        :user: User instance will own the new created item
        :values: Dictionary with values for the new item
        :returns: Instance of clazz

        """
        if not isinstance(values, dict):
            raise ValueError("Values must be a dictionary")
        item = self._clazz()
        # Try to set the ownership of the entry if the item provides the
        # fields.
        if (hasattr(item, 'uid') and
           user is not None):
            item.uid = user.id
        if (hasattr(item, 'gid')):
            modul = get_item_modul(None, item)
            if modul.default_gid:
                item.gid = modul.default_gid
            elif (user is not None and user.default_gid):
                item.gid = user.default_gid
        if values:
            if hasattr(self, "_use_strict"):
                item.set_values(values, use_strict=self._use_strict)
            else:
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
