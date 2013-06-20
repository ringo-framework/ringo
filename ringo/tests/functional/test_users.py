import unittest
from sqlalchemy.orm.exc import NoResultFound
from ringo.model.user import User
from ringo.tests import BaseFunctionalTest

class TestUser(BaseFunctionalTest):

    def test_wrong_url(self):
        self.login('admin', 'secret')
        self.app.get('/users/listtest', status=404)

    def test_list(self):
        self.login('admin', 'secret')
        self.app.get('/users/list', status=200)

    def test_read(self):
        self.login('admin', 'secret')
        self.app.get('/users/read/1', status=200)

    def test_read_unknown(self):
        self.login('admin', 'secret')
        try:
            self.app.get('/users/read/1234')
        except NoResultFound:
            return True
        # Must fail!
        self.assertEqual(0,1)

    def test_create(self):
        self.login('admin', 'secret')
        self.app.get('/users/create', status=200)

    def test_create_save_fail(self):
        self.login('admin', 'secret')
        # fail because password missmatch!
        values = {
            'login': 'testuser',
            'activation_token': '',
            'password': '12345678',
            'retype_password': '123456789'
        }
        self.app.post('/users/create', values, status=200)

    def test_create_save_success(self):
        self.login('admin', 'secret')
        # fail because password missmatch!
        values = {
            'login': 'testuser',
            'activation_token': '',
            'password': '12345678',
            'retype_password': '12345678'
        }
        self.app.post('/users/create', values, status=302)

    def test_edit(self):
        self.login('admin', 'secret')
        self.app.get('/users/update/1', status=200)

    def test_edit_save_ok(self):
        self.login('admin', 'secret')
        values = {
            'login': 'admin',
            'groups': '1',
            'gid': '',
            'activated': 'True',
            'activation_token': ''
        }
        self.app.post('/users/update/1', values, status=302)

    def test_edit_save_fail(self):
        self.login('admin', 'secret')
        values = {
            'login': '',
            'groups': '1',
            'gid': '',
            'activated': 'True',
            'activation_token': ''
        }
        self.app.post('/users/update/1', values, status=200)

    def test_delete(self):
        last_id = self.get_max_id(User)
        self.login('admin', 'secret')
        self.app.get('/users/delete/%s' % last_id, status=200)

    def test_delete_confirmed(self):
        last_id = self.get_max_id(User)
        self.login('admin', 'secret')
        values = {'confirmed': '1'}
        self.app.post('/users/delete/%s' % last_id, values, status=302)

    def test_delete_fail(self):
        last_id = self.get_max_id(User)
        self.login('admin', 'secret')
        values = {'confirmed': '0'}
        self.app.post('/users/delete/%s' % last_id, values, status=200)

if __name__ == '__main__':
    unittest.main()
