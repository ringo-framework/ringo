from operator import itemgetter
from formbar.config import Config, load
from ringo.lib.helpers import get_path_to_form_config
from ringo.model import DBSession

class BaseItem(object):

    _table_fields = []
    _modul_id = None

    def __str__(self):
        return self.__unicode__()

    def __getitem__(self, name):
        return getattr(self, name)

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
    def get_table_config(cls):
        return cls._table_fields

    @classmethod
    def get_form_config(cls, formname):
        cfile = "%s.xml" % cls.__tablename__
        config = Config(load(get_path_to_form_config(cfile)))
        return config.get_form(formname)

    @classmethod
    def get_action_routename(cls, action):
        return "%s-%s" % (cls.__tablename__, action)


class BaseList(object):
    def __init__(self, clazz, db):
        self.clazz = clazz
        self.items = db.query(clazz).all()

    def sort(self, field, order):
        sorted_items = sorted(self.items, key=itemgetter(field))
        if order == "desc":
            sorted_items.reverse()
        self.items = sorted_items


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

    def load(self, id, db=None):
        """Loads the item with id from the database and returns it.

        :id: ID of the item to be loaded
        :db: DB session to load the item
        :returns: Instance of clazz

        """
        if db is None:
            db = DBSession
        return db.query(self._clazz).filter(self._clazz.id == id).one()
