import logging
from pyramid.security import remember, forget
from pyramid.httpexceptions import HTTPFound
from ringo.lib.sql.db import NTDBSession as db
from ringo.model.user import User

log = logging.getLogger(__name__)

ANONYMOUS_USER = None


def user_factory(handler, registry):
    global ANONYMOUS_USER
    if ANONYMOUS_USER is None:
        login = registry.settings.get("auth.anonymous_user")
        ANONYMOUS_USER = db.query(User).filter(User.login == login).one()

    def user_tween(request):
        if not request.user:
            log.info("Anonymous login")
            request.user = ANONYMOUS_USER
            request.session["auth.anonymous_user"] = ANONYMOUS_USER.login
            request.session.save()
            target_url = request.route_path('home')
            headers = remember(request, ANONYMOUS_USER.id)
            return HTTPFound(location=target_url, headers=headers)
        return handler(request)
    return user_tween


def ensure_logout(handler, registry):
    def user_tween(request):
        anon_login = request.session.get("auth.anonymous_user")
        if request.user and anon_login == request.user.login:
            log.info("Anonymous logout")
            headers = forget(request)
            target_url = request.route_path('home')
            return HTTPFound(location=target_url, headers=headers)
        return handler(request)
    return user_tween
