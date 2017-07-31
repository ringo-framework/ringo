import logging
import sys
from sqlalchemy.orm.exc import NoResultFound
from pyramid.security import remember, forget
from pyramid.httpexceptions import HTTPFound
from ringo.lib.sql.db import NTDBSession as db
from ringo.lib.cache import init_cache
from ringo.model.user import User
from ringo.config import static_urls

log = logging.getLogger(__name__)

ANONYMOUS_USER = None


def user_factory(handler, registry):
    global ANONYMOUS_USER
    if ANONYMOUS_USER is None:
        login = registry.settings.get("auth.anonymous_user")
        try:
            ANONYMOUS_USER = db.query(User).filter(User.login == login).one()
        except NoResultFound:
            log.error("Misconfigured anonymous user '{}'. User not found.".format(login))
            sys.exit(1)

    def user_tween(request):
        if static_urls.match(request.path):
            return handler(request)
        # Cache must be existing. Because we are in a tween this code
        # is executed _before_ the "NewRequest" event is handled in the
        # application which usually ensures that the cache is
        # initialised. So we will "pre"-init the cache here.
        init_cache(request)
        if not request.user:
            # Do not (re)-authorize the user on logout and autologout
            # pages.
            if request.path not in [request.route_path("autologout"),
                                    request.route_path("logout")]:
                request.user = ANONYMOUS_USER
                request.session["auth.anonymous_user"] = ANONYMOUS_USER.login
                request.session.save()
                headers = remember(request, ANONYMOUS_USER.id)
                return HTTPFound(location=request.path, headers=headers)
        return handler(request)
    return user_tween


def ensure_logout(handler, registry):
    def user_tween(request):
        anon_login = request.session.get("auth.anonymous_user")
        init_cache(request)
        if anon_login and request.user and (request.user.login == anon_login):
            headers = forget(request)
            del request.session["auth.anonymous_user"]
            request.session.save()
            target_url = request.route_path('home')
            return HTTPFound(location=target_url, headers=headers)
        return handler(request)
    return user_tween
