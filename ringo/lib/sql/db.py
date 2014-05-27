import query
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
