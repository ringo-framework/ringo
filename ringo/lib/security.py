import logging
import hashlib

from pyramid.security import unauthenticated_userid
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from sqlalchemy.orm.exc import NoResultFound

from ringo.model import DBSession
from ringo.model.user import User

log = logging.getLogger(__name__)


def setup_ringo_security(config):
    authn_policy = AuthTktAuthenticationPolicy('seekrit', hashalg='sha512')
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
        try:
            user = request.db.query(User).filter_by(id=userid).one()
            return user
        except NoResultFound:
            pass
    return None


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
