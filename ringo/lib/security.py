import logging
import hashlib
import uuid
import string
import random
from datetime import datetime

from pyramid.events import ContextFound
from pyramid.security import unauthenticated_userid,\
    has_permission as has_permission_,\
    Allow, ALL_PERMISSIONS
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.httpexceptions import HTTPUnauthorized

from sqlalchemy.orm.exc import NoResultFound

from ringo.lib.sql import DBSession
from ringo.model.base import BaseItem
from ringo.model.user import User, PasswordResetRequest

log = logging.getLogger(__name__)


def password_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


def csrf_token_validation(event):
    request = event.request
    csrf = request.params.get('csrf_token')
    if (request.method == 'POST'):
        if (csrf != unicode(request.session.get_csrf_token())):
            raise HTTPUnauthorized


def setup_ringo_security(config):
    authn_policy = AuthTktAuthenticationPolicy('seekrit',
                                               hashalg='sha512',
                                               callback=get_principals)
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    # Make the user object available as attribute "user" in the request.
    # See http://docs.pylonsproject.org/projects/ \
    #            pyramid_cookbook/en/latest/auth/ \
    #            user_object.html
    config.set_request_property(get_user, 'user', reify=True)

    # Add subscriber to check the CSRF token in POST requests.
    config.add_subscriber(csrf_token_validation, ContextFound)


def get_user(request):
    userid = unauthenticated_userid(request)
    if userid is not None:
        return _load_user(userid, request)
    return None


def has_permission(permission, context, request):
    """Wrapper for pyramid's buitin has_permission function.  This
    wrapper sets dynamically the __acl__ attribute of the given context
    and then  .  check if the user has the given permission in the
    current context using pyramid's has_permission function.

    Context can be:
    * Instance of BaseItem
    * Subclass of BaseItem
    * Ressource, built from a RessourceFactory

    If context is an instance or subclass of BaseItem the wrapper will
    dynamically set the __acl__ attribute. This attribute is used by the
    pyramid's has_permission function the check the permission. If the
    context is a resource the function does nothing as the resource
    already has the __acl__ attribute set.

    If the user has the permission the it returns True, else False
    (Actually it returns a boolean like object, see pyramids
    has_permission doc for more details.)

    :permission: String. Name of the permission. E.g list, create, read
    :context: Either Resource, Instance of BaseItem or Subclass of BaseItem
    :request: current request
    :returns: True or False (Boolean like object)

    """
    if isinstance(context, BaseItem):
        modul = context.get_item_modul()
        context.__acl__ = get_permissions(modul, context)
    #elif issubclass(context.__class__, BaseItem):
    # Checking for subclass of BaseItem does not work always to check
    # for a get_item_modul function.
    elif hasattr(context, "get_item_modul"):
        modul = context.get_item_modul()
        context.__acl__ = get_permissions(modul)
    return has_permission_(permission, context, request)


def get_permissions(modul, item=None):
    """Will return a list permissions attached to the modul and
    optionally to particular item of the modul. The returned list is
    suitable for using it as ACL in pyramid's authorization system.  The
    function will at least return class based permissions. If a item is
    provided then additional item level permissions are returned.

    The function will iterate over all available actions of the given
    modul and tries to adds a permission entry to the for every role
    which has granted access to the action.

    For every role it will check the following things:

    1. If the role is marked as "administrational" role, then add the
       permission for role and action.
    2. Elif action is either "list" or "create" (permissons on class
       level) then add the permission for the role and action.
    3. Elif an item is provided add item level permissions for the role
       _and_ only the owner or users which are member of the items group.

    :model: The modul for which the permissions are returned
    :item: Optional: Item of the model for which the permissons as
           returned
    :returns: List of permissions
    """
    perms = []
    # Default permisson. Admins should be allowed to to everything.
    perms.append((Allow, 'role:admin', ALL_PERMISSIONS))
    if not modul:
        return perms
    for action in modul.actions:
        for role in action.roles:
            default_principal = 'role:%s' % role
            # administrational role means allow without further
            # ownership checks.
            if role.admin is True:
                perms.append((Allow, default_principal, action.name.lower()))
            # class level permissions
            elif action.name.lower() in ['create', 'list']:
                perms.append((Allow, default_principal, action.name.lower()))
            # item level permissions. Only allow the owner or members of
            # the items group.
            elif item and hasattr(item, 'uid'):
                principal = default_principal + ';uid:%s' % item.uid
                perms.append((Allow, principal, action.name.lower()))
                principal = default_principal + ';group:%s' % item.gid
                perms.append((Allow, principal, action.name.lower()))
    return perms


def get_principals(userid, request):
    """Returns a list of pricipals for the user with userid for the
    given request.

    Principals are basically strings naming the groups or roles the user have.
    Example: role:admin or group:users are typical principals.

    :userid: id of the user
    :request: current request
    :returns: list with pricipals

    """
    user = _load_user(userid, request)
    principals = []
    if user:
        # Add roles the user have
        for role in get_roles(user):
            principals.append('role:%s' % role.name)
            principals.append('role:%s;uid:%s' % (role.name, user.id))
        # Add groups the user member of
        for group in user.groups:
            principals.append('group:%s' % group.id)
            for role in get_roles(user):
                principals.append('role:%s;group:%s' % (role.name, group.id))
        # Finally add the user itself
        principals.append('uid:%s' % user.id)
    log.debug('Principals for userid "%s": %s' % (userid, principals))
    return principals

# ROLES
#######


def has_role(user, role):
    """Return True if the user has the given role. Else False"
    :user: User instance
    :returns: True or False
    """
    return user.has_role(role)


def get_roles(user):
    """Returns a list of roles the user has. The list contains
    `Role` object and are collected by loading roles directly
    attached to the user plus roles attached to the groups the user
    is member of

    :user: User instance
    :returns: List of `Role` instances

    """
    return user.get_roles()

# GROUPS
########


def has_group(user, group):
    """Return True if the user is in the the given group. Else False"
    :user: User instance
    :returns: True or False
    """

    groups = [g.name for g in user.groups]
    return group in groups

# Helpers
#########


def _load_user(userid, request):
    try:
        factory = User.get_item_factory()
        return factory.load(userid)
    except NoResultFound:
        return None


def activate_user(token, db):
    """Will check if confirmation token is valid by searching a user
    with this activation token. If a user is found the activated flag
    will be set to true.

    :token: confirmation token
    :db: db connection
    :returns: user
    """
    try:
        user = db.query(User).filter_by(activation_token=token).one()
        user.activated = True
        user.activation_token = None
        log.info('User %s activated' % user)
        return user
    except NoResultFound:
        log.warning('User activation failed for token %s'
                    % (token))
        return None


def password_reset(token, db):
    """Will check if there is a password reset token is valid. The
    function will reset the password of the user. The new generated
    password is returned.

    :token: password reset token
    :db: db connection
    :returns: tupe of user and password
    """
    try:
        token = db.query(PasswordResetRequest).filter_by(token=token).one()
        # Check that the token is not outdated
        td = datetime.now() - token.created
        if td.days <= 1:
            user = token.user
            password = password_generator()
            md5_pw = hashlib.md5()
            md5_pw.update(password)
            md5_pw = md5_pw.hexdigest()
            user.password = md5_pw
            log.info('Password reset success for user %s' % user)
            # delete all old password request token
            for old_token in user.reset_tokens:
                db.delete(old_token)
            return user, password
        else:
            log.warning('Password reset failed for token %s (outdated)'
                        % token)
            return None, None
    except NoResultFound:
        log.warning('Password reset failed for token %s' % token)
        return None, None


def request_password_reset(username, db):
    """Will check if there is a user with the given username and creates
    a new entry in the password_reset table with a new token. The new
    token is than returned. If there is no user with the username then
    do nothing and return None.

    :username: username
    :db: db connection
    :returns: User

    """
    user = None
    try:
        user = db.query(User).filter_by(login=username).one()
        log.info('Password reset request for user %s' % user)
        reset_token = PasswordResetRequest(str(uuid.uuid4()))
        user.reset_tokens.append(reset_token)
    except NoResultFound:
        log.warning('Password reset request for non existing user %s'
                    % username)
    return user


def login(username, password):
    """Returns a `User` instance if the login does not fail with the
    given login and password.

    :username: username as String
    :password: password as SHA1 encrypted string
    :returns: `User` instance if login is OK else None.

    """
    md5_pw = hashlib.md5()
    md5_pw.update(password or "")
    md5_pw = md5_pw.hexdigest()
    log.debug("Login user '%s' with pw '%s'" % (username, password))
    try:
        user = DBSession.query(User).filter_by(login=username,
                                               password=md5_pw).one()
        if user.activated:
            log.info("Login successfull '%s'" % (username))
            return user
        log.info("Login failed for user '%s'. "
                 "Reason: Not activated" % username)
    except NoResultFound:
        log.info("Login failed for user '%s'. "
                 "Reason: Username or Password wrong" % username)
    return None
