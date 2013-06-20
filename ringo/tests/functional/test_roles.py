import unittest
from sqlalchemy.orm.exc import NoResultFound
from ringo.model.user import Role
from ringo.tests import BaseFunctionalTest


class TestRole(BaseFunctionalTest):

    def test_wrong_url(self):
        self.login('admin', 'secret')
        self.app.get('/roles/listtest', status=404)

    def test_list(self):
        self.login('admin', 'secret')
        self.app.get('/roles/list', status=200)

    def test_sort(self):
        self.login('admin', 'secret')
        values = {
            'sort_field': 'name',
            'sort_order': 'desc'
        }
        self.app.get('/roles/list', values, status=200)

    def test_read(self):
        self.login('admin', 'secret')
        self.app.get('/roles/read/1', status=200)

    def test_read_unknown(self):
        self.login('admin', 'secret')
        try:
            self.app.get('/roles/read/1234')
        except NoResultFound:
            return True
        # Must fail!
        self.assertEqual(0,1)

    def test_create(self):
        self.login('admin', 'secret')
        self.app.get('/roles/create', status=200)

    def test_create_save_fail(self):
        self.login('admin', 'secret')
        # fail because name must not be none!
        values = {
            'name': ''
        }
        self.app.post('/roles/create', values, status=200)

    def test_create_save_success(self):
        self.login('admin', 'secret')
        values = {
            'name': 'testrole',
            'admin': 'True'
        }
        self.app.post('/roles/create', values, status=302)

    def test_edit(self):
        self.login('admin', 'secret')
        self.app.get('/roles/update/1', status=200)

    def test_edit_save_ok(self):
        self.login('admin', 'secret')
        values = {
            'name': 'admin',
            'admin': 'True'
        }
        self.app.post('/roles/update/1', values, status=302)

    def test_edit_save_fail(self):
        self.login('admin', 'secret')
        # Missing value
        values = {
            'name': ''
        }
        self.app.post('/roles/update/1', values, status=200)

    def test_delete(self):
        last_id = self.get_max_id(Role)
        self.login('admin', 'secret')
        self.app.get('/roles/delete/%s' % last_id, status=200)

    def test_delete_confirmed(self):
        last_id = self.get_max_id(Role)
        self.login('admin', 'secret')
        values = {'confirmed': '1'}
        self.app.post('/roles/delete/%s' % last_id, values, status=302)

    def test_delete_fail(self):
        last_id = self.get_max_id(Role)
        self.login('admin', 'secret')
        values = {'confirmed': '0'}
        self.app.post('/roles/delete/%s' % last_id, values, status=200)

if __name__ == '__main__':
    unittest.main()
