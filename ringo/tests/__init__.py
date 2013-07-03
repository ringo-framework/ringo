import os
import unittest
#from mock import Mock
from paste.deploy.loadwsgi import appconfig
from webtest import TestApp

from pyramid import testing

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker

from ringo.lib.sql import DBSession
from ringo import main
from ringo.lib.i18n import locale_negotiator


here = os.path.dirname(__file__)
try:
    settings = appconfig('config:' + os.path.join(here, '../../', 'test.ini'))
except IOError:
    # Issue #22. Silently igonore this error if there is no test.ini
    pass



class BaseTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = engine_from_config(settings, prefix='sqlalchemy.')
        cls.Session = sessionmaker()

    def setUp(self):
        connection = self.engine.connect()

        # begin a non-ORM transaction
        self.trans = connection.begin()

        # bind an individual Session to the connection
        #DBSession.configure(bind=connection)
        self.session = self.Session(bind=connection)

    def tearDown(self):
        # rollback - everything that happened with the
        # Session above (including calls to commit())
        # is rolled back.
        testing.tearDown()
        self.trans.rollback()
        self.session.close()


#class BaseUnitTest(BaseTestCase):
#    def setUp(self):
#        self.config = testing.setUp(request=testing.DummyRequest())
#        super(BaseUnitTest, self).setUp()
#
#    def get_csrf_request(self, post=None):
#        csrf = 'abc'
#
#        if not u'csrf_token' in post.keys():
#            post.update({
#                'csrf_token': csrf
#            })
#
#        request = testing.DummyRequest(post)
#
#        request.session = Mock()
#        csrf_token = Mock()
#        csrf_token.return_value = csrf
#
#        request.session.get_csrf_token = csrf_token
#
#        return request


class BaseFunctionalTest(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = main({}, **settings)
        super(BaseFunctionalTest, cls).setUpClass()

    def setUp(self):
        self.app = TestApp(self.app)
        self.config = testing.setUp()
        super(BaseFunctionalTest, self).setUp()

    def login(self, username, password, status=302):
        '''Will login the user with username and password. On default we we do
        a check on a successfull login (status 302).'''
        self.logout()
        response = self.app.post('/auth/login',
            params={'login': username,
                    'pass': password},
            status=status
        )
        return response

    def logout(self):
        'Logout the currently logged in user (if any)' 
        response = self.app.get('/auth/logout',
            params={},
            status=302
        )
        return response

    def get_max_id(self, clazz):
        'Returns the max id of item (last inserted) of clazz'
        items = clazz.get_item_list(self.session)
        last_item = items.items[-1]
        return last_item.id
