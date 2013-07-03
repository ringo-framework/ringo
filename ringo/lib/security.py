import logging
import hashlib
import uuid
import string
import random
from datetime import datetime

from pyramid.security import unauthenticated_userid,\
    has_permission as has_permission_
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from sqlalchemy.orm.exc import NoResultFound

from ringo.lib.sql import DBSession
from ringo.model.user import User, PasswordResetRequest

log = logging.getLogger(__name__)


def password_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


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


def has_permission(permission, context, request):
    return has_permission_(permission, context, request)


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
        # Add groups the user member of
        for group in user.groups:
            principals.append('group:%s' % group.name)
        # Finally add the user itself
        principals.append('uid:%s' % user.id)


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
