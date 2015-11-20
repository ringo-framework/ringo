import os
import pytest


# DB fixtures
@pytest.fixture(scope="module")
def engine(request, db_connect_url, app_config):
    if app_config:
        from sqlalchemy import engine_from_config
        #engine_from_config(get_settings(), prefix='sqlalchemy.')
        engine = engine_from_config(app_config)
    elif db_connect_url:
        from sqlalchemy.engine import create_engine
        engine = create_engine(db_connect_url)
    else:
        raise RuntimeError("Can not establish a connection to the database")

    def fin():
        print ("Disposing engine")
        engine.dispose()

    request.addfinalizer(fin)
    return engine


@pytest.fixture(scope="module")
def connection(request, engine):
    connection = engine.connect()
    def fin():
        print ("Closing connection")
        connection.close()

    request.addfinalizer(fin)
    return connection


@pytest.fixture()
def transaction(request, connection):
    """Will start a transaction on the connection. The connection will
    be rolled back after it leaves its scope."""
    transaction = connection.begin()

    def fin():
        print ("Rollback")
        transaction.rollback()

    request.addfinalizer(fin)
    return connection


@pytest.fixture()
def dbsession(request, connection):
    from sqlalchemy.orm import sessionmaker
    return sessionmaker()(bind=connection)


@pytest.fixture()
def config(registry, apprequest):
    from pyramid import testing
    config = testing.setUp(registry, request=apprequest)
    return config


@pytest.fixture(scope="session")
def registry(app_config):
    from pyramid.registry import Registry
    name = app_config.context.distribution.project_name
    registry = Registry(name)
    registry.settings = app_config
    return registry

@pytest.fixture(scope="session")
def app(app_config):
    from webtest import TestApp
    name = app_config.context.distribution.project_name
    app = __import__(name).main({}, **app_config)
    return TestApp(app)


@pytest.fixture()
def apprequest(dbsession):
    from mock import Mock
    from pyramid import testing
    from ringo.lib.cache import Cache
    request = testing.DummyRequest()
    request.cache_item_modul = Cache()
    request.cache_item_list = Cache()

    user = Mock()
    user.news = []
    user.settings = {'searches': {'foo': 'bar'}}

    request.user = user

    request.accept_language = Mock(return_value="en")
    request.translate = lambda x: x
    request.db = dbsession
    request.context = Mock()
    request.session.get_csrf_token = lambda: "xxx"
    return request

from pyramid import testing
testing.setUp()


# Config options
@pytest.fixture(scope="session")
def db_connect_url(request):
    return request.config.getoption("--db-connect-url")


@pytest.fixture(scope="session")
def app_config(request):
    from paste.deploy.loadwsgi import appconfig
    config = request.config.getoption("--app-config")
    if config:
        return appconfig('config:' + os.path.abspath(config))
    else:
        return None

def pytest_addoption(parser):
    parser.addoption("--db-connect-url", action="store",
                     default=None,
                     help="Name of the database to connect to")
    parser.addoption("--app-config", action="store",
                     default=None,
                     help="Path to the application config file")


