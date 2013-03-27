from formbar.config import Config, load
from ringo.lib.helpers import get_path_to_form_config
from ringo.model.meta import MetaItem


class BaseItem(object):

    _table_fields = []
    _modul_id = None

    def __str__(self):
        return self.__unicode__()

    @classmethod
    def get_item_factory(cls):
        return BaseFactory(cls)

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


class BaseFactory(object):

    def __init__(self, clazz):
        """Factory to create of load instances of the clazz.

        :clazz: The clazz of which new items will be created

        """
        self._clazz = clazz

    def create(self, user):
        """Will create a new instance of clazz. The instance is it is not saved
        persistent at this moment. The method will also take care of
        creating a MetaItem.

        :user: User instance will own the new created item
        :returns: Instance of clazz

        """
        mid = self._clazz._modul_id
        uid = None
        gid = None
        if user is not None:
            uid = user.id
            gid = user.gid
        meta = MetaItem(mid=mid, uid=uid, gid=gid)
        item = self._clazz()
        item.meta = meta
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
