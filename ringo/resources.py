import logging
from sqlalchemy.orm.exc import NoResultFound
from ringo.lib.security import get_permissions

log = logging.getLogger(__name__)


def get_resource_factory(clazz, modul=None):
    """Dynamically create a Resource factory. The modul can be provided
    optionally to optimize loading additional data from the database. It
    prevents extra loading of the modul later."""
    name = clazz.__name__
    factory = type(name,
                   (RessourceFactory, ),
                   {'__model__': clazz, '__modul__': modul})
    return factory


class RessourceFactory(object):

    def __init__(self, request, item=None):
        # Reset ACL
        self.__acl__ = []
        self.item = item

        item_id = request.matchdict.get('id')
        if item_id and not self.item:
            self.item = self._load_item(item_id)
        self.__acl__ = self._get_item_permissions(request)

    def _load_item(self, id):
        """Will load an item from the given clazz. The id of the item to
        load is taken from the request matchdict. If no item can be found an
        Exception is raised.

        :id: id of the item to be loaded.
        :returns: Loaded item

        """
        # TODO: Make loading items more robust in RessourceFactory. This
        # is needed in case that a Ressource is build for a clazz which
        # is not related to the  the current request which has an id. In
        # this case loading the item might fail if there is no item with
        # the id in the request.
        #
        # If think this code might cause problems as trying to build a
        # build a Ressource with an independet request smells a
        # littlebit. Better add a flag to to ignore the id in the
        # request in such cases.
        try:
            factory = self.__model__.get_item_factory()
            return factory.load(id)
        except NoResultFound:
            return None

    def _get_item_permissions(self, request):
        if not self.__modul__:
            self.__modul__ = self.__model__.get_item_modul()
        return get_permissions(self.__modul__, self.item)
