import unittest
import transaction

from pyramid import testing
from pyramid import paster

from ringo.model import DBSession, Base
from ringo.model.modul import (
    init_model as init_modul_model,
)
from ringo.model.user import (
    init_model as init_user_model
)


class TestInit(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)

        with transaction.manager:
            init_modul_model(DBSession)
            init_user_model(DBSession)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

class TestFunctional(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        # TODO: Setup creating a testdatabase.
        app = paster.get_app('test.ini')
        #Base.metadata.create_all(DBSession.get_bind())
        from webtest import TestApp
        self.testapp = TestApp(app)

    @classmethod
    def tearDownClass(self):
        del self.testapp
        #Base.metadata.drop_all(DBSession.get_bind())
        #DBSession.remove()

    def login(self, username, password, status=302):
        '''Will login the user with username and password. On default we we do
        a check on a successfull login (status 302).'''
        self.logout()
        response = self.testapp.post('/auth/login',
            params={'login': username,
                    'pass': password},
            status=status
        )
        return response

    def logout(self):
        'Logout the currently logged in user (if any)' 
        response = self.testapp.get('/auth/logout',
            params={},
            status=302
        )
        return response
