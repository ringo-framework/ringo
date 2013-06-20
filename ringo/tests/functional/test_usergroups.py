import unittest
from sqlalchemy.orm.exc import NoResultFound
from ringo.model.user import Usergroup
from ringo.tests import BaseFunctionalTest

class TestUsergroup(BaseFunctionalTest):

    def test_wrong_url(self):
        self.login('admin', 'secret')
        self.app.get('/usergroups/listtest', status=404)

    def test_list(self):
        self.login('admin', 'secret')
        self.app.get('/usergroups/list', status=200)

    def test_read(self):
        self.login('admin', 'secret')
        self.app.get('/usergroups/read/1', status=200)

    def test_read_unknown(self):
        self.login('admin', 'secret')
        try:
            self.app.get('/usergroups/read/1234')
        except NoResultFound:
            return True
        # Must fail!
        self.assertEqual(0,1)

    def test_create(self):
        self.login('admin', 'secret')
        self.app.get('/usergroups/create', status=200)

    def test_create_save_fail(self):
        self.login('admin', 'secret')
        # fail because name must not be none!
        values = {
            'name': ''
        }
        self.app.post('/usergroups/create', values, status=200)

    def test_create_save_success(self):
        self.login('admin', 'secret')
        # fail because password missmatch!
        values = {
            'name': 'testusergroup',
            "roles":"1",
            "members":"1"
        }
        self.app.post('/usergroups/create', values, status=302)

    def test_edit(self):
        self.login('admin', 'secret')
        self.app.get('/usergroups/update/1', status=200)

    def test_edit_save_ok(self):
        self.login('admin', 'secret')
        values = {
            "name":"admins",
            "roles":"1",
            "members":"1"
        }
        self.app.post('/usergroups/update/1', values, status=302)

    def test_edit_save_fail(self):
        self.login('admin', 'secret')
        # Missing values.
        values = {
            "name":"",
            "roles":"1",
            "members":"1"
        }
        self.app.post('/usergroups/update/1', values, status=200)

    def test_delete(self):
        self.login('admin', 'secret')
        last_id = self.get_max_id(Usergroup)
        self.login('admin', 'secret')
        self.app.get('/usergroups/delete/%s' % last_id, status=200)

    def test_delete_confirmed(self):
        self.login('admin', 'secret')
        last_id = self.get_max_id(Usergroup)
        values = {'confirmed': '1'}
        self.app.post('/usergroups/delete/%s' % last_id, values, status=302)

    def test_delete_fail(self):
        self.login('admin', 'secret')
        last_id = self.get_max_id(Usergroup)
        values = {'confirmed': '0'}
        self.app.post('/usergroups/delete/%s' % last_id, values, status=200)

if __name__ == '__main__':
    unittest.main()
