import logging
import transaction
import re
import datetime
from operator import itemgetter
from formbar.config import Config, load
from sqlalchemy.orm import joinedload, ColumnProperty, class_mapper
from ringo.lib.helpers import get_path_to_form_config
from ringo.lib.sql import DBSession, regions
from ringo.lib.sql.query import FromCache, set_relation_caching

log = logging.getLogger(__name__)


class BaseItem(object):

    _modul_id = None
    """Configure a list of relations which are configured to be joined
    in the query"""
    _sql_joined_relations = []
    # TODO: Defining relations which should be cached seems to be
    # ignored for lazy load. So the only way of caching those
    # relations too is to put them in the SQL-JOIN and to a cached
    # query. This way all relations are cached to.
    """Configure a list of relations which are configured to be
    cached"""
    _sql_cached_realtions = []
    """Cached table config for the class"""
    _cache_table_config = None

    def __str__(self):
        return self.__unicode__()

    def __getitem__(self, name):
        return self.get_value(name)

    def __json__(self, request):
        rvalue = {}
        for col in self.get_columns():
            value = getattr(self, col)
            # FIXME: If value is type date it can not be serialized.
            if isinstance(value, datetime.date):
                value = str(value)
            rvalue[col] = value
        return rvalue

    @classmethod
    def get_columns(cls):
        return [prop.key for prop in class_mapper(cls).iterate_properties
            if isinstance(prop, ColumnProperty)]

    @classmethod
    def get_item_factory(cls):
        return BaseFactory(cls)

    @classmethod
    def get_item_list(cls, db):
        return BaseList(cls, db)

    @classmethod
    def get_item_modul(cls):
        from ringo.model.modul import ModulItem
        factory = BaseFactory(ModulItem)
        return factory.load(cls._modul_id)

    @classmethod
    def get_table_config(cls, tablename=None):
        from ringo.lib.renderer import TableConfig
        if not cls._cache_table_config:
            cls._cache_table_config = TableConfig(cls, tablename)
        return cls._cache_table_config


    @classmethod
    def get_form_config(cls, formname):
        """Return the Configuration for a given form. The configuration
        tried to be loaded from the application first. If this fails it
        tries to load it from the ringo application."""
        cfile = "%s.xml" % cls.__tablename__
        try:
            loaded_config = load(get_path_to_form_config(cfile))
        except IOError:
            loaded_config = load(get_path_to_form_config(cfile, 'ringo'))
        config = Config(loaded_config)
        return config.get_form(formname)

    @classmethod
    def get_action_routename(cls, action, prefix=None):
        routename = "%s-%s" % (cls.__tablename__, action)
        if prefix:
            return "%s-%s" % (prefix, routename)
        return routename

    def get_value(self, name, form_id="create"):
        """Return the value of the given attribe of the item. Unlike
        accessing the raw value through the attribite directly this
        function will apply all configured transformations to the value
        before returing it."""
        raw_value = getattr(self, name)
        expand = []
        table_config = self.get_table_config()
        # TODO: Iterating again and again over the columns might be
        # expensive. Do some caching here? (None) <2013-09-22 20:33> 
        for col in table_config.get_columns():
            if col.get('expand'):
                expand.append(col.get('name'))
        if name in expand:
            form_config = self.clazz.get_form_config(form_id)
            field_config = form_config.get_field(name)
            for option in field_config.options:
                if str(raw_value) == str(option[1]):
                    return option[0]
        return raw_value


class BaseList(object):
    def __init__(self, clazz, db, user=None, cache=""):
        """
        A List object of. A list can be filterd, and sorted.

        :clazz: Class of items which will be loaded.
        :db: DB session to load the item
        :user: If provided only items readable for the
        given user are included in the list
        :cache: Name of the cache region. If empty then no caching is
        done.
        """
        self.clazz = clazz
        # TODO: Check which is the best loading strategy here for large
        # collections. Tests with 100k datasets rendering only 100 shows
        # that the usual lazyload method seems to be the fastest which is
        # not what if have been expected.
        #self.items = db.query(clazz).options(joinedload('*')).all()

        q = db.query(self.clazz)
        if cache in regions.keys():
            q = set_relation_caching(q, self.clazz, cache)
            q = q.options(FromCache(cache))
        for relation in self.clazz._sql_cached_realtions:
            q = q.options(joinedload(relation))

        self.items = self._filter_for_user(q.all(), user)
        self.search_filter = []

    def _filter_for_user(self, items, user):
        """Returns a filterd item list. The items are filterd based on
        the permission of the given user. Only items are included where
        the given user has read access. This means:

         1. The user has aproriate role (read access)
         2. Is owner or member of the items group 

        If no user is provided the list is not filtered and all origin
        items are included in the returned list.
        """
        # Filter items based on the uid
        filtered_items = []
        if user and not user.has_role("admin"):
            # TODO: Check if the user has the role to read items of the
            # clazz. If not then we do not need to check any further as
            # the user isn't allowed to see the item anyway. (torsten)
            # <2013-08-22 08:06>
            groups = [g.id for g in user.groups]


            # Iterate over all items and check if the user has generally
            # access to the item.
            for item in items:
                # Only check ownership if the item provides a uid.
                # Is owner?
                if hasattr(item, 'uid'):
                    # Is owner?
                    if item.uid == user.id:
                        filtered_items.append(item)
                    # Is in group?
                    elif item.gid in groups:
                        filtered_items.append(item)
                else:
                    filtered_items.append(item)
            return filtered_items
        else:
            return items

    def __json__(self, request):
        return self.items

    def sort(self, field, order):
        sorted_items = sorted(self.items, key=itemgetter(field))
        if order == "desc":
            sorted_items.reverse()
        self.items = sorted_items

    def filter(self, filter_stack):
        """This function will filter the list of items by only leaving
        those items in the list which match all search criterias in the
        filter stack. The list will get reduced with every iteration on
        the filter stack.

        For each filter in the stack The search word will be compiled to
        the regular expression. Then all items are iterated.  For each
        item the function will try to match the value of either all, or
        from the configued search field with the regular expression. If
        the value matches, then the item is kept in the list.
        """
        self.search_filter = filter_stack
        for search, search_field in filter_stack:
            # Build a regular expression
            re_expr = re.compile(search)
            filtered_items = []
            log.debug('Filtering "%s" in "%s" on %s items'
                      % (search, search_field, len(self.items)))
            if search_field != "":
                fields = [search_field]
            else:
                table_config = self.clazz.get_table_config()
                fields = [field.get('name') for field in table_config.get_columns()]
            for item in self.items:
                for field in fields:
                    value = item.get_value(field)
                    if isinstance(value, list):
                        value = ", ".join([unicode(x) for x in value])
                    else:
                        value = unicode(value)
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

    def create(self, user):
        """Will create a new instance of clazz. The instance is it is not saved
        persistent at this moment. The method will also take care of
        setting the correct ownership.

        :user: User instance will own the new created item
        :returns: Instance of clazz

        """
        item = self._clazz()
        # Try to set the ownership of the entry if the item provides the
        # fields.
        if (hasattr(item, 'uid')
        and hasattr(item, 'gid')
        and user is not None):
            item.uid = user.id
            item.gid = user.gid
        return item

    def load(self, id, db=None, cache=""):
        """Loads the item with id from the database and returns it.

        :id: ID of the item to be loaded
        :db: DB session to load the item
        :cache: Name of the cache region. If empty then no caching is
        done.
        :returns: Instance of clazz

        """
        if db is None:
            db = DBSession
        q = db.query(self._clazz)
        if cache in regions.keys():
            q = set_relation_caching(q, self._clazz, cache)
            q = q.options(FromCache(cache))
        for relation in self._clazz._sql_joined_relations:
            q = q.options(joinedload(relation))
        return q.filter(self._clazz.id == id).one()
