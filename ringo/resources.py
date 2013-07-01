import logging
from sqlalchemy.orm.exc import NoResultFound
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

    def _set_default_acl(self):
        self.__acl__.extend(self.__default_acl__)

    def _get_role_permissions(self, request):
        """Will return a list the assigned permissions for the current
        user in the request.

        If the a role of a user is an administrational role thean all
        permissions to this role are added to the returned list without
        checking any ownership. 
        If it is not an administrational role, the "list" and "create"
        actions are added in all cases. Item related action like "edit",
        "delete" or "read" are only added if the current user is
        actually the owner.

        :request: current request
        :returns: List of Action items (Permissions)

        """
        permissions = []
        user = request.user
        if user is None:
            return []
        for role in get_roles(user):
            log.debug("Setting permissions for role %s" % role)
            for perm in role.permissions:
                if perm.modul.id == self.__model__._modul_id:
                    permission = None
                    if role.admin == True:
                        # Set administrational role based permissions. For
                        # administrational roles no ownership is
                        # checked an the user will get all permissions which are
                        # assigned to the role.
                        permission = (Allow, 'role:%s' % role, perm.name.lower())
                    else:
                        # Set user roles based permission. In contrast to the
                        # administrational roles the user will only get the permissions
                        # assigned to the role if he is the owner of the
                        # item or if the action is "list" of "create".
                        if perm.name.lower() in ['list', 'create']:
                            permission = (Allow, 'role:%s' % role, perm.name.lower())
                        elif self.item:
                            permission = (Allow, 'uid:%s' % self.item.uid, perm.name.lower())
                    if permission:
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
