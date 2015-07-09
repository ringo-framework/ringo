import logging
import query
from pyramid.events import NewRequest
from sqlalchemy import engine_from_config
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy import exc
from sqlalchemy import event
from sqlalchemy.pool import Pool

from ringo.lib.sql.cache import regions, init_cache

init_cache()

log = logging.getLogger(__name__)

# Session initialisation
########################
# scoped_session.  Apply our custom CachingQuery class to it,
# using a callable that will associate the dictionary
# of regions with the Query.
DBSession = scoped_session(
                sessionmaker(
                    query_cls=query.query_callable(regions),
                    extension=ZopeTransactionExtension()
                )
            )

NTDBSession = scoped_session(
                sessionmaker(
                    query_cls=query.query_callable(regions)
                )
            )


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
    return engine_from_config(settings, 'sqlalchemy.')

def setup_db_session(engine):
    DBSession.configure(bind=engine)
    NTDBSession.configure(bind=engine)

# Session initialisation
########################
def setup_connect_on_request(config):
    config.add_subscriber(connect_on_request, NewRequest)


def connect_on_request(event):
    request = event.request
    request.db = DBSession
    request.add_finished_callback(close_db_connection)


def close_db_connection(request):
    request.db.close()
