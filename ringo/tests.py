import hashlib
import unittest
import transaction

from pyramid import testing

from ringo.model import DBSession
from ringo.model.user import init_model as init_user_model, User


class TestMyView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        from .models import (
            Base,
            MyModel,
        )
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        with transaction.manager:
            model = MyModel(name='one', value=55)
            DBSession.add(model)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_it(self):
        from .views import my_view
        request = testing.DummyRequest()
        info = my_view(request)
        self.assertEqual(info['one'].name, 'one')
        self.assertEqual(info['project'], 'ringo')


class TestUserModel(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        from .models import (
            Base,
        )
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        with transaction.manager:
            init_user_model(DBSession)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_userlist(self):
        result = DBSession.query(User).all()
        self.assertEqual(len(result), 1)

    def test_username(self):
        result = DBSession.query(User).all()
        self.assertEqual(result[0].login, 'admin')

    def test_password(self):
        m = hashlib.md5()
        m.update('secret')
        result = DBSession.query(User).all()
        self.assertEqual(result[0].password, m.hexdigest())
