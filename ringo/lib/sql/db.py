import sys
import logging
import query
from zope.sqlalchemy import ZopeTransactionExtension
from pyramid.events import NewRequest
from sqlalchemy import engine_from_config
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import exc
from sqlalchemy import event
from sqlalchemy.pool import Pool, StaticPool

from ringo.lib.sql.cache import regions, init_cache

log = logging.getLogger(__name__)

# Session initialisation
########################
# scoped_session.  Apply our custom CachingQuery class to it,
# using a callable that will associate the dictionary
# of regions with the Query.
DBSession = scoped_session(
                sessionmaker(
                    query_cls=query.query_callable(regions),
                )
            )

NTDBSession = scoped_session(
                sessionmaker(
                    query_cls=query.query_callable(regions)
                )
            )
testsession = None


# Pessimisitic detection of disconnects of connections in the connection pool
# (E.g the database server restarts because of maintenance. Per checkout
# of a connection from the pool we will do a extra SQL-Query. In case
# this fails because of the disconnection the connection pool will be
# invalidated and the connections will be reestablished. See
# http://docs.sqlalchemy.org/en/latest/core/pooling.html#disconnect-handling-pessimistic
# for for details.
@event.listens_for(Pool, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
    except:
        log.info("Possible DB disconnect detected! "
                 "Reestablishing the connection to the DB.")
        # optional - dispose the whole pool
        # instead of invalidating one at a time
        connection_proxy._pool.dispose()

        # raise DisconnectionError - pool will try
        # connecting again up to three times before raising.
        raise exc.DisconnectionError()
    cursor.close()


def setup_db_engine(settings):
    cachedir = settings.get("db.cachedir")
    regions = []
    for region in settings.get("db.cacheregions", "").split(" "):
        regions.append(region.split(":"))
    if cachedir:
        init_cache(cachedir, regions)
    if settings.get("app.mode") == "testing":
        return engine_from_config(settings, 'sqlalchemy.',
                                  poolclass=StaticPool)
    else:
        return engine_from_config(settings, 'sqlalchemy.')


def setup_db_session(engine, settings=None):
    # Onyl use ZopeTransactionExtension if not in testmode to prevent
    # autocommits after each request.
    if not settings:
        settings = {}
    if settings.get("app.mode") == "testing":
        DBSession.configure(bind=engine)
    else:
        DBSession.configure(bind=engine, extension=ZopeTransactionExtension())
    NTDBSession.configure(bind=engine)


# Session initialisation
########################
def setup_session_on_request(config):
    if config.registry.settings.get("app.mode") == "testing":
        config.add_subscriber(add_test_session_to_request, NewRequest)
        # Add exception view to rollback the database in case of
        # errors in testmode. Adding a view here feels wrong, but it is
        # the currently  only known way to to handle exceptions.
        config.add_view(rollback_on_exception, context=Exception)
    else:
        config.add_subscriber(add_session_to_request, NewRequest)


def rollback_on_exception(exc, request):
    """If the application is in testing mode, this view will be called
    on every exeption and takes care that the current transaction is
    rolled back."""
    request.db.rollback()
    request.db.close()
    # Reraise the origin exception without loosing the stacktrace.
    raise sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]


def add_test_session_to_request(event):
    global testsession
    request = event.request
    if testsession is not None:
        request.db = testsession
        request._active_testcase = True
    elif request.params.get("_testcase") == "begin":
        testsession = DBSession()
        request.db = testsession
        request._active_testcase = True
    else:
        request.db = DBSession()
        request._active_testcase = False
    request.add_finished_callback(close_test_session)


def close_test_session(request):
    global testsession
    if testsession is not None:
        if request.params.get("_testcase") == "end":
            log.debug("End Testcase")
            request.db.rollback()
            request.db.close()
            testsession = None
        else:
            request.db.flush()
    else:
        request.db.commit()


def add_session_to_request(event):
    request = event.request
    request.db = DBSession()
    request.add_finished_callback(close_session)


def close_session(request):
    if request.db:
        request.db.close()
