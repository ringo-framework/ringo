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


class TestLoginView(unittest.TestCase):
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

    def test_login(self):
        from .views import login
        request = testing.DummyRequest()
        result = login(request)
        self.assertEqual(result.status, '200 OK')

    def test_login_ok(self):
        from .views import login
        request = testing.DummyRequest(post={})
        result = login(request)
        self.assertEqual(result.status, '301 OK')

    def test_login_fail(self):
        from .views import login
        request = testing.DummyRequest()
        result = login(request)
        self.assertEqual(result.status, '200 OK')


class TestDefaultAdminUser(unittest.TestCase):
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

    def test_defaultusergroup(self):
        result = DBSession.query(User).all()
        self.assertEqual(result[0].default_group.name, 'admins')

    def test_groups(self):
        result = DBSession.query(User).all()
        self.assertEqual(len(result[0].groups), 1)
        self.assertEqual(result[0].groups[0].name, 'admins')

    def test_roles(self):
        result = DBSession.query(User).all()
        self.assertEqual(len(result[0].get_roles()), 1)
        self.assertEqual(result[0].get_roles()[0].name, 'admin')

    def test_permissions(self):
        result = DBSession.query(User).all()
        role = result[0].get_roles()[0]
        self.assertEqual(len(role.permissions), 4)
        self.assertEqual(role.permissions[0].name, 'create')
        self.assertEqual(role.permissions[1].name, 'read')
        self.assertEqual(role.permissions[2].name, 'update')
        self.assertEqual(role.permissions[3].name, 'delete')
