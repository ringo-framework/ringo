import logging
import hashlib
import uuid

from pyramid.security import unauthenticated_userid
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from sqlalchemy.orm.exc import NoResultFound

from ringo.model import DBSession
from ringo.model.user import User, password_reset_requests

log = logging.getLogger(__name__)


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


def get_user(request):
    userid = unauthenticated_userid(request)
    if userid is not None:
        return _load_user(userid, request)
    return None


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
        for role in get_roles(user):
            principals.append('role:%s' % role.name)
    log.debug('Principals for user "%s": %s' % (user.login, principals))
    return principals

# ROLES
#######


def has_role(user, role):
    """Return True if the user has the given role. Else False"
    :user: User instance
    :returns: True or False
    """

    roles = [r.name for r in get_roles(user)]
    return role in roles


def get_roles(user):
    """Returns a list of roles the user has. The list contains
    `Role` object and are collected by loading roles directly
    attached to the user plus roles attached to the groups the user
    is member of

    :user: User instance
    :returns: List of `Role` instances

    """
    tmp_roles = {}

    # Add roles directly attached to the user.
    for role in user.roles:
        if role.name not in tmp_roles:
            tmp_roles[role.name] = role

    # Add roles directly attached to the user.
    for group in user.groups:
        for role in group.roles:
            if role.name not in tmp_roles:
                tmp_roles[role.name] = role

    return list(tmp_roles.values())

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
        user = request.db.query(User).filter_by(id=userid).one()
        return user
    except NoResultFound:
        return None


def request_password_reset(username):
    """Will check if there is a user with the given username and creates
    a new entry in the password_reset table with a new token. The new
    token is than returned. If there is no user with the username then
    do nothing and return None.

    :username: username
    :returns: password request token.

    """
    token = None
    try:
        user = DBSession.query(User).filter_by(login=username).one()
        log.warning('Password reset request for user %s' % user)
        token = str(uuid.uuid4())
        # Insert the token and the username into the password_reset
        # table
        ins = password_reset_requests.insert().values(login=username,
                                                      token=token)
        # FIXME: Entry is not created.
        DBSession.execute(ins)
        DBSession.flush()

    except NoResultFound:
        log.warning('Password reset request for non existing user %s'
                    % username)
    return token


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
        log.info("Login successfull '%s'" % (username))
        return user
    except NoResultFound:
        log.info("Login failed for user '%s'" % username)
        return None
