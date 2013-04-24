import logging
from pyramid.security import (
    Allow,
    ALL_PERMISSIONS
)
from ringo.lib.security import get_roles

log = logging.getLogger(__name__)


def get_resource_factory(clazz):
    """Dynamically create a Resource factory"""
    name = clazz.__name__
    factory = type(name, (RessourceFactory, ), {'__model__': clazz})
    return factory


class RessourceFactory(object):

    # Users with the admin role should be allowed to to all actions
    __default_acl__ = [(Allow, 'role:admin', ALL_PERMISSIONS)]

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
        log.debug("Setting ACL for user %s" % request.user)
        self._set_default_acl()
        # Set role based permissions
        user = request.user
        for role in get_roles(user):
            log.debug("Setting permissions for role %s" % role)
            for perm in role.permissions:
                if perm.modul.id == self.__model__._modul_id:
                    permission = (Allow, 'role:%s' % role, perm.name.lower())
                    log.debug("adding new permission: %s" % str(permission))
                    self.__acl__.append(permission)

        # Row bases permission checks: Check if the current user is the
        # owner of the item and the modul has information abouts the
        # owner (id > 5, starts with profiles)
        if self.item and self.__model__._modul_id > 5:
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
