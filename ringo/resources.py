import logging
from sqlalchemy.orm.exc import NoResultFound
from ringo.lib.security import get_permissions

log = logging.getLogger(__name__)


def get_resource_factory(clazz):
    """Dynamically create a Resource factory"""
    name = clazz.__name__
    factory = type(name, (RessourceFactory, ), {'__model__': clazz})
    return factory


class RessourceFactory(object):

    def __init__(self, request):
        # Reset ACL
        self.__acl__ = []
        self.item = None

        item_id = request.matchdict.get('id')
        if item_id:
            self.item = self._load_item(item_id)
        self.__acl__ = self._get_item_permissions(request)

    def _load_item(self, id):
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
        modul = self.__model__.get_item_modul()
        return get_permissions(modul, self.item)


class Resource(object):
    """Ressource element"""

    __name__ = ""
    __parent__ = None

    # Default ACL
    #__acl__ = [(Allow, 'role:admin', ('create', 'read', 'update',
    #                                  'delete', 'list'))]

    def __init__(self, title=None, model=None):
        self._childs = {}
        self._title = title
        self._model = title

    def add_child(self, url, resource):
        resource.__name__ = url
        resource.__parent__ = self
        self._childs[url] = resource

    def __getitem__(self, name):
        log.debug('Searching for resource "%s" in %s' % (name, self._childs))
        try:
            resource = self._childs[name]
            return resource
        except KeyError:
            raise


class Root(Resource):
    def __init__(self, request):
        super(Root, self).__init__("Root")
        self.request = request
