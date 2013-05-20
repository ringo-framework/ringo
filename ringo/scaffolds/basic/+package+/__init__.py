from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from ringo import DBSession
from ringo.model import Base


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    # Include basic ringo configuration.
    config.include('ringo')
    config.commit()

    # Now configure the application and optionally overwrite previously
    # done configurations.
    config.scan()
    return config.make_wsgi_app()
