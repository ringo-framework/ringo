import unittest
from ringo.tests import TestFunctional

#class TestEncryptPassword(TestFunctional):
#    def test_encrypt_password(self):
#        # self.assertEqual(expected, encrypt_password(request, user))
#        assert False # TODO: implement your test here

class TestUser(TestFunctional):
    def test_list(self):
        self.login('admin', 'secret')
        self.testapp.get('/users/list', status=200)

    def test_read(self):
        self.login('admin', 'secret')
        self.testapp.get('/users/read/1', status=200)

if __name__ == '__main__':
    unittest.main()
