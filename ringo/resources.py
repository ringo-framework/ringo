import logging
from pyramid.security import (
    Allow,
)

log = logging.getLogger(__name__)


def get_resource_factory(clazz):
    factory = RessourceFactory
    factory.__model__ = clazz
    return factory


class RessourceFactory(object):

    __model__ = None

    # Users with the admin role should be allowed to to all actions
    __default_acl__ = [(Allow, 'role:admin', ('create', 'read', 'update',
                                      'delete', 'list'))]

    def __init__(self, request):
        # Reset ACL
        self.__acl__ = []
        self.item = None
        item_id = request.matchdict.get('id')
        if item_id:
            self.item = self._load_item(item_id)
        self._set_acl(request)

    def _load_item(self, id):
        factory = self.__model__.get_item_factory()
        return factory.load(id)

    def _set_default_acl(self):
        self.__acl__.extend(self.__default_acl__)

    def _set_acl(self, request):
        # Row bases permission checks: Check if the current user is the
        # owner of the item
        self._set_default_acl()
        if self.item:
            uid = self.item.uid
            permission = (Allow, 'uid:%s' % uid, ('create', 'read', 'update',
                                                  'delete', 'list'))
            log.debug("adding new permission: %s" % str(permission))
            self.__acl__.append(permission)

class Resource(object):
    """Ressource element"""

    __name__ = ""
    __parent__ = None

    # Default ACL
    __acl__ = [(Allow, 'role:admin', ('create', 'read', 'update',
                                      'delete', 'list'))]

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
