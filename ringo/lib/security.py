import logging
import hashlib
import uuid
import string
import random
from passlib.context import CryptContext
from datetime import datetime
from pyramid.events import ContextFound, NewRequest
from pyramid.security import unauthenticated_userid, \
    has_permission as has_permission_, \
    Allow, ALL_PERMISSIONS
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.httpexceptions import HTTPUnauthorized
from sqlalchemy.orm.exc import NoResultFound
from ringo.lib.helpers import get_item_modul, dynamic_import
from ringo.lib.sql import DBSession
from ringo.lib.alchemy import get_relations_from_clazz
from ringo.model.base import BaseItem
from ringo.model.modul import ModulItem
from ringo.model.user import User, PasswordResetRequest, Login

log = logging.getLogger(__name__)


def password_generator(size=12, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


def get_anonymous_user(settings):
    """Will return the name of the configured anonymous user if there is
    one. Else return None."""
    return settings.get("auth.anonymous_user")


def get_auth_timeout(settings):
    """Will return the amount of seconds until the auth session will
    time out. This can be configured in the application ini file. If no
    configuration is found. it defaults to 1800 seconds (30min)"""
    return int(settings.get("auth.timeout") or 1800)


def get_auth_timeout_warning(settings):
    """Will return the amount of seconds before a warning dialog will be
    raised before the session will time out. This can be configured in
    the application ini file. If no configuration is found. it defaults
    to 30 seconds"""
    return int(settings.get("auth.timeout_warning") or 30)


def get_cookie_secret(settings):
    """Will return the configured string in the config to sign the
    cookies. If no string is configured. Generate a random string for
    this."""
    secret = settings.get("security.cookie_secret")
    if not secret:
        secret = password_generator(50)
    return secret


pwd_context = CryptContext(
    # replace this list with the hash(es) you wish to support.
    # this example sets pbkdf2_sha256 as the default,
    # with support for legacy md5 hashes.
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",

    # vary rounds parameter randomly when creating new hashes...
    all__vary_rounds=0.1,

    # set the number of rounds that should be used...
    # (appropriate values may vary for different schemes,
    # and the amount of time you wish it to take)
    pbkdf2_sha256__default_rounds=8000,
)


def encrypt_password(password, scheme=None):
    """Will return a string with encrypted password using the passlib
    library. The returned string will have the following format:
    $algo$rounds$salt$hash

    :password: unencrypted password
    :scheme: string of an supported encryption algorithm. Defaults tthe
    CryptContext default
    :returns: encrypted password

    """
    return pwd_context.encrypt(password, scheme=scheme)


def verify_password(password, pwhash):
    """Will return True if the password is valid. Else False.

    :password: unencrypted password
    :pwhash: encrypted password
    :returns: True or False
    """
    if pwhash.startswith("$"):
        return pwd_context.verify(password, pwhash)
    else:
        # Old password hash scheme without salt etc.
        md5_pw = hashlib.md5()
        md5_pw.update(password)
        return pwhash == md5_pw.hexdigest()


def passwords_needs_update(pwhash):
    """Will return True if the given pwhash uses a deprecated
    encryption algorithm and needs to be updated.

    :pwhash: encrypted password
    :returns: True or False
    """
    if pwhash.startswith("$"):
        return pwd_context.needs_update(pwhash)
    else:
        # Old password hash scheme without salt etc.
        return True


def load_user(login):
    """Will return the user with the given login
    name. If no user can be found with the given login "None" will be
    returned.

    :login: Login of the user as string
    :returns: User or None

    """
    return DBSession.query(User).filter_by(login=login).scalar()


def csrf_token_validation(event):
    request = event.request
    if (request.method == 'POST'):
        csrf = request.params.get('csrf_token')
        if (csrf != unicode(request.session.get_csrf_token())):
            log.warning("CSRF token check failed. Raising 401 exception.")
            raise HTTPUnauthorized


def refresh_auth_cookie(event):
    """This fuction will refresh the the timeout of the authentification
    cookie. See
    https://groups.google.com/forum/#!topic/pylons-discuss/HczvAEd5xY8
    for more details.
    """
    event.request.unauthenticated_userid


def setup_ringo_security(config):
    settings = config.registry.settings
    timeout = get_auth_timeout(settings) + 5
    secret = get_cookie_secret(settings)
    secure = settings.get("security.cookie_secure", "false") == "true"
    include_ip = settings.get("security.cookie_ip", "false") == "true"
    path = settings.get("security.cookie_path", "/")
    domain = settings.get("security.cookie_domain")
    httponly = settings.get("security.cookie_httponly", "false") == "true"
    cookie_name = settings.get("security.cookie_name", "auth_tkt")
    authn_policy = AuthTktAuthenticationPolicy(secret,
                                               secure=secure,
                                               hashalg='sha512',
                                               timeout=timeout,
                                               reissue_time=timeout / 10,
                                               callback=get_principals,
                                               include_ip=include_ip,
                                               path=path,
                                               domain=domain,
                                               http_only=httponly,
                                               cookie_name=cookie_name)
    authz_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authz_policy)
    config.set_authentication_policy(authn_policy)
    # Make the user object available as attribute "user" in the request.
    # See http://docs.pylonsproject.org/projects/ \
    #            pyramid_cookbook/en/latest/auth/ \
    #            user_object.html
    config.add_request_method(get_user, 'user', reify=True)

    # Add subscriber to check the CSRF token in POST requests. You can
    # disable this for testing by setting the
    # "security.enable_csrf_check" config variable to "false".
    if settings.get('security.enable_csrf_check', 'true') != "false":
        config.add_subscriber(csrf_token_validation, ContextFound)
    # Refresh the auth cookie timeout on every request. On default this
    # would only happen on requests which needs
    # authentification/authorisation. As the authentification should be
    # valid as long the user shows some activity by triggering requests
    # this tween will refresh the timeout on every request.
    config.add_subscriber(refresh_auth_cookie, NewRequest)

    # Add tweens to add custom security headers.
    # http://ghaandeeonit.tumblr.com/post/65698553805/securing-your-pyramid-application
    if settings.get("security.header_secure", "true") == "true":
        config.add_tween('ringo.tweens.secure_headers.secure_headers_factory')
    if settings.get("security.header_clickjacking", "true") == "true":
        config.add_tween('ringo.tweens.clickjacking.clickjacking_factory')
    if settings.get("security.header_csp", "false") == "true":
        config.add_tween('ringo.tweens.csp.csp_factory')
    if get_anonymous_user(settings):
        log.info("Setting up anonymous access.")
        config.add_tween('ringo.tweens.anonymous_access.user_factory')
    else:
        config.add_tween('ringo.tweens.anonymous_access.ensure_logout')


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
    if isinstance(context, BaseItem) or hasattr(context, "_modul_id"):
        modul = get_item_modul(request, context)
        context.__acl__ = context._get_permissions(modul, context, request)
    # Call of has_permission will trigger 4 additional SQL-Queries. The
    # query will only be trigger once per request.
    return has_permission_(permission, context, request)


def get_permissions(modul, item=None):
    """Will return a list permissions attached to the modul and
    optionally to particular item of the modul. The returned list is
    suitable for using it as ACL in pyramid's authorization system.  The
    function will at least return class based permissions. If a item is
    provided then additional item level permissions are returned.

    Note that item can also be a class and not an instance. In this case
    the class level permissions are returned

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

    # Load current states for the item as we need to check which
    # permissions the user has depending on the current states of the item.
    current_states = []
    if isinstance(item, BaseItem) and hasattr(item, '_statemachines'):
        for smname in item._statemachines:
            sm = item.get_statemachine(smname)
            state = sm.get_state()
            current_states.append(state)

    # No need to call get_item_actions. We only need the modul actions
    # here as all other ActionItem added dynamically to the items clazz
    # (e.g Mixin actions), will map their permission to one of the
    # available base modul permissions (create, read, update, delete...)
    actions = modul.actions
    for action in actions:
        permission = action.permission or action.name.lower()
        # TODO: Note that actions, which are not inserted into the
        # database (e.g custom mixin actions.) will not have any roles
        # and are not considerd on building principals yet. (ti)
        # <2014-02-07 11:08>
        for role in action.roles:
            add_perm = True
            default_principal = 'role:%s' % role.name

            # Check if the actions is available in the current state of
            # the item if the item has states.
            for state in current_states:
                if str(action.name.lower()) in state.get_disabled_actions(role.name):
                    add_perm = False
                    continue

            # administrational role means allow without further
            # ownership checks. If item is class than check is on modul
            # level.
            if (role.admin is True or action.admin is True) and add_perm:
                perms.append((Allow, default_principal, permission))

            # Modul level (class level) permissions.
            # Always add the default principals for the create and list
            # actions as those actions can not be checked on item level
            # anyway.
            elif permission in ['create', 'list']:
                perms.append((Allow, default_principal, permission))

            # If the item is not an instance of a BaseItem then add
            # we want to get the permission on modul
            # level too. So again add the default principal
            elif not isinstance(item, BaseItem) and add_perm:
                perms.append((Allow, default_principal, permission))

            # If the item has a uuid the we want get the permission on
            # Item level. Only allow the owner or members of the items
            # group.
            elif item and hasattr(item, 'uid') and add_perm:
                principal = default_principal + ';uid:%s' % item.uid
                perms.append((Allow, principal, permission))
                principal = default_principal + ';group:%s' % item.gid
                perms.append((Allow, principal, permission))

    return perms


def __add_principal(principals, new):
    if new not in principals:
        principals.append(new)
    return principals


def get_principals(userid, request):
    """Returns a list of pricipals for the user with userid for the
    given request.

    Principals are basically strings naming the groups or roles the user have.
    Example: role:admin or group:users are typical principals.

    :userid: id of the user
    :request: current request
    :returns: list with pricipals

    """
    if request.user:
        user = request.user
    else:
        user = _load_user(userid, request)
    principals = []
    if user:
        # Add the roles of the user. The roles will be added in
        # connection with the uid and groups as the roles should only be
        # applicable if the user is the owner or member of the group of
        # the item.
        for urole in user.roles:
            principal = 'role:%s' % urole.name
            __add_principal(principals, principal)
            principal = 'role:%s;uid:%s' % (urole.name, user.id)
            __add_principal(principals, principal)
            for group in user.groups:
                # Add the user role for every group the user is member
                # of
                principal = 'role:%s;group:%s' % (urole.name, group.id)
                __add_principal(principals, principal)
        # Finally add the user itself
        principal = 'uid:%s' % user.id
        __add_principal(principals, principal)
    principals.sort(key=len, reverse=True)
    log.debug('Principals for userid "%s": %s' % (userid, principals))
    return principals


# ROLES
#######


def has_role(user, role):
    """Return True if the user has the given role. Else False"
    :user: User instance
    :returns: True or False
    """
    if user is None:
        return False
    return user.has_role(role)


def has_admin_role(action_name, clazz, request):
    """Return True if the current user has admin role for the given
    action_name on the given clazz. Having a admin role means that the
    check for the ownership in context of the permissions checks can be
    omitted.

    :action_name: Name of the action
    :clazz: clazz
    :request: current request and user
    :returns: True or False
    """
    modul = get_item_modul(request, clazz)
    for action in modul.actions:
        if action.name.lower() == action_name:
            for role in action.roles:
                if role.admin and has_role(request.user, role.name):
                    return True
    return False


def get_roles(user):
    """Returns a list of roles the user has. The list contains
    `Role` object and are collected by loading roles directly
    attached to the user plus roles attached to the groups the user
    is member of

    :user: User instance
    :returns: List of `Role` instances

    """
    return user.roles


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
        modul = get_item_modul(request, User)
        UserClazz = dynamic_import(modul.clazzpath)
        factory = UserClazz.get_item_factory()
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
        user.activation_token = ""
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
            user.password = encrypt_password(password)
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
    log.debug("Login user '%s' with pw '%s'" % (username, password))
    user = load_user(username)
    if user:
        if verify_password(password, user.password):
            if user.activated:
                Login(user, success=True)
                user.last_login = datetime.utcnow()
                log.info("Login successfull '%s'" % (username))
                if passwords_needs_update(user.password):
                    log.info("Updating password for user '%s'" % (username))
                    user.password = encrypt_password(password)
                return user
            else:
                Login(user, success=False)
                log.info("Login failed for user '%s'. "
                         "Reason: Not activated" % username)
                return user
        else:
            Login(user, success=False)
            log.info("Login failed for user '%s'. "
                     "Reason: Wrong password" % username)
    else:
        log.info("Login failed for user '%s'. "
                 "Reason: Username not known" % username)
    return None


def get_last_successfull_login(request, user):
    if user is not None:
        result = request.db.query(Login) \
            .filter(Login.success == True, Login.uid == user.id) \
            .order_by(Login.datetime.desc()) \
            .limit(2).all()
        if len(result) > 1:
            return result[1]
    return None


def get_last_failed_login(request, user):
    result = None
    if user is not None:
        result = request.db.query(Login) \
            .filter(Login.success == False, Login.uid == user.id) \
            .order_by(Login.datetime.desc()) \
            .first()
    return result


def get_last_logins(request, since, success=None):
    """Returns a list of last logins since the given datetime.

    :request: Current request
    :since: Datetime object
    :success: Boolean flag to indicate to only return successfull or
              failed logins. If None all logins are returned.
    :returns: List of Login items

    """
    if request.user is None:
        return []

    result = request.db.query(Login) \
        .filter(Login.datetime > since, Login.uid == request.user.id) \
        .order_by(Login.id.desc()) \
        .all()
    if success is None:
        return result
    else:
        return [l for l in result if l.success == success]


class AuthentificationException(Exception):
    """Exception to be raise if error on authentification is detected."""
    pass


class AuthorizationException(Exception):
    """Exception to be raise if a authorization error is detected."""
    pass


class ValueChecker(object):
    """Checks the permission of a user to set values, provided by an
    dictionary, in an item.

    This checker restricts users to only set the values which they may
    also read. This prevents the possible security thread
    of gaining higher privileges by setting forbidden values with a
    manipulated requests.

    This espacially important for values which will change relations in
    the item. For each relation of the item the function will iterate
    over the values in the dictionary and check if the user is at least
    allowed to read the value.

    If the user is not allowed to read a value the checker will either

     * Raise an AuthorizationException if strict mode is enabled, or
     * Filter the set of values based on the permissions.

    In all cases a warning is logged if the Checker detects a permission
    violation. This class implements a very important security check and
    should be always used before values are about to be changed in an
    item.

    Limitations:
    The function currently only checks permissions on values which are
    about to be set in a sqlalchemy.orm.relation. This means setting the
    values directly in a FK is still possible.
    """

    def __init__(self, strict=True):
        self.strict = strict
        """Mode of the checker. If strict is true a
        AuthorizationException will be raised if a permission violation
        is detected. Otherwise the values get filtered."""

    def check(self, clazz, values, request, item=None):
        """Will do permission checks on the values. If strict mode is
        disabled the function will do the following:

         * For new added relations the fuction will remove every
           relation from to the values for which the user is not granted
           read access.
         * For removed relations the function will re-add every relation
           to the values for which the user is not granted read access.

        The function will return the values after checking and
        filtering. If strict mode is enabled an AuthorizationException
        is raised.

        :clazz: The clazz of the item which is about to be changed
        :values: Dictionary with deserialised and validated form values.
        :request: Current request
        :item: Defaults to None. If provided than the checker will only
        check differences between the values to be set and already
        present in the item. Else all values are checked.
        """
        for relation in get_relations_from_clazz(clazz):
            # If the relation is not set in the values then continue, as
            # we do not need to check anything.
            if relation not in values:
                continue

            # Get old and new values.
            # For the purpose to unify the test logic of the permissions
            # checks the values will be converted into a list in all
            # cases. In case of N:1 realtions new_values will be a
            # single item and not a list.  In all other cases (1:N, N:N)
            # new_values is a list.
            new_values = values[relation]
            if not isinstance(new_values, list):
                new_values = [new_values]

            if item is not None:
                old_values = item.get_value(relation)
                if not isinstance(old_values, list):
                    old_values = [old_values]
            else:
                old_values = []

            # Determine the values which actually need to be checked.
            # If no item is provided, all values are checked. Otherwise
            # only changed values are checked.
            if item is None:
                to_check = [(v, 0) for v in new_values]
            else:
                to_check = self._diff(old_values, new_values)

            # Now iterate over all value which need to be checked.
            for value, modifier in to_check:
                # If the relation is a ModulItem or is not a Baseitem at
                # all also do no checks.
                # Modulitem do not have any uid or gid which will allow
                # checking permissions. Allowing links to a modul item
                # is currently not known to be a security thread.
                if (isinstance(value, ModulItem)
                    or has_permission("link", value, request)
                    or not isinstance(value, BaseItem)):
                    continue
                else:
                    if modifier > 0:
                        action = "add"
                    elif modifier < 0:
                        action = "remove"
                    else:
                        action = "set"
                    msg = ("User '%s' is not allowed to %s %s %s from %s %s"
                           % (request.user.login, action, type(value),
                              value.id, clazz, getattr(item, "id", '')))
                    log.warning(msg)
                    if self.strict:
                        raise AuthorizationException(msg)
                    else:
                        raise NotImplementedError()
        return values

    def _diff(self, old, new):
        """Will diff the values of old and new. It returns a list of
        tuples with values

          * Which are exclusive in new (value has been added)
          * Which are exclusive in old (value has been removed)

        The tuple will contain the value and 1 for added values and -1
        for removed items.
        """
        diff = []
        if isinstance(old, list):
            old = set(old)
            new = set(new)
            # Get added
            for added in new.difference(old):
                diff.append((added, 1))
            # Get removed
            for removed in old.difference(new):
                diff.append((removed, -1))
            return diff
        else:
            if old != new:
                if old is not None:
                    diff.append((old, -1))
                if new is not None:
                    diff.append((new, 1))
            return diff
