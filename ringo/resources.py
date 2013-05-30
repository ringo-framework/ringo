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

    def _get_role_permissions(self, request, admin=False):
        """@todo: Will return the assigned permissions for the current user in the request.

        :request: current request
        :admin: Returns permissions of the administrational roles. Else
        return permissons from user role.
        :returns: List of Action items (Permissions)

        """
        permissions = []
        user = request.user
        if user is None:
            return []
        for role in get_roles(user):
            if role.admin != admin: continue
            log.debug("Setting permissions for role %s" % role)
            for perm in role.permissions:
                if perm.modul.id == self.__model__._modul_id:
                    if admin:
                        permission = (Allow, 'role:%s' % role, perm.name.lower())
                    else:
                        permission = (Allow, 'uid:%s' % self.item.uid, perm.name.lower())
                    log.debug("adding new permission: %s" % str(permission))
                    permissions.append(permission)
        return permissions

    def _set_acl(self, request):
        """Will dynamically set the __acl__ for this ressource for the current request.

        :request: current request
        :returns: None

        """
        log.debug("Setting ACL for user %s" % request.user)
        self._set_default_acl()
        # Set administrational role based permissions. For
        # administrational roles no ownership is
        # checked an the user will get all permissions which are
        # assigned to the role.
        self.__acl__.extend(self._get_role_permissions(request, admin=True))

        # Set user roles based permission. In contrast to the
        # administrational roles the user will only get the permissions
        # assigned to the role if he is the owner of the item.
        # Check if the current user is the owner of the item and the
        # modul has information abouts the owner (id > 5, starts with
        # profiles)
        if self.item and self.__model__._modul_id > 5:
            self.__acl__.extend(self._get_role_permissions(request))


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
