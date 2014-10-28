import query
from pyramid.events import NewRequest
from sqlalchemy import engine_from_config
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from ringo.lib.sql.cache import regions, init_cache

init_cache()

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
