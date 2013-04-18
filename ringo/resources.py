import logging
from pyramid.security import (
    Allow,
)

log = logging.getLogger(__name__)

def bootstrap(request):
    root = Resource("Root")
    test = Resource("Test")
    test2 = Resource("Test2")
    test.add_child("xxx", test2)
    root.add_child("testtraversal", test)
    return root

def get_resource_factory(clazz):
    factory = RessourceFactory
    factory.__model__ = clazz
    return factory


class RessourceFactory(object):

    __model__ = None
    __acl__ = [(Allow, 'role:admin', ('create', 'read', 'update',
                                      'delete', 'list'))]

    def __init__(self, request):
        self._set_acl(request)

    def _set_acl(self, request):
        pass

class Resource(object):
    """Ressource element"""

    __name__ = ""
    __parent__ = None

    # Default ACL
    __acl__ = [(Allow, 'role:admin', ('create', 'read', 'update',
                                      'delete', 'list'))]

    def __init__(self, title=None):
        self._childs = {}
        self._title = title
        #self.request = request

    def add_child(self, url, resource):
        resource.__name__ = url
        resource.__parent__ = self
        self._childs[self.__name__] = resource

    def __getitem__(self, name):
        log.debug('Searching for resource "%s" in %s' % (name, self._childs))
        try:
            resource = self._childs[name]
        except KeyError:
            raise
