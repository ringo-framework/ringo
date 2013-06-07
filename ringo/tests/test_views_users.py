import unittest
from sqlalchemy.orm.exc import NoResultFound
from ringo.tests import TestFunctional

#class TestEncryptPassword(TestFunctional):
#    def test_encrypt_password(self):
#        # self.assertEqual(expected, encrypt_password(request, user))
#        assert False # TODO: implement your test here

class TestUser(TestFunctional):

    def test_wrong_url(self):
        self.login('admin', 'secret')
        self.testapp.get('/users/listtest', status=404)

    def test_list(self):
        self.login('admin', 'secret')
        self.testapp.get('/users/list', status=200)

    def test_read(self):
        self.login('admin', 'secret')
        self.testapp.get('/users/read/1', status=200)

    def test_read_unknown(self):
        self.login('admin', 'secret')
        try:
            self.testapp.get('/users/read/2')
        except NoResultFound:
            return True
        # Must fail!
        self.assertEqual(0,1)

    def test_create(self):
        self.login('admin', 'secret')
        self.testapp.get('/users/create', status=200)

    def test_edit(self):
        self.login('admin', 'secret')
        self.testapp.get('/users/update/1', status=200)

    def test_delete(self):
        self.login('admin', 'secret')
        self.testapp.get('/users/delete/1', status=200)

if __name__ == '__main__':
    unittest.main()
