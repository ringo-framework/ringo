import unittest
from sqlalchemy.orm.exc import NoResultFound
from ringo.model.user import Profile
from ringo.tests import BaseFunctionalTest

class TestProfile(BaseFunctionalTest):

    def test_wrong_url(self):
        self.login('admin', 'secret')
        self.app.get('/profiles/listtest', status=404)

    def test_list(self):
        self.login('admin', 'secret')
        self.app.get('/profiles/list', status=200)

    def test_read(self):
        self.login('admin', 'secret')
        self.app.get('/profiles/read/1', status=200)

    def test_read_unknown(self):
        self.login('admin', 'secret')
        try:
            self.app.get('/profiles/read/1234')
        except NoResultFound:
            return True
        # Must fail!
        self.assertEqual(0,1)

    def test_edit(self):
        self.login('admin', 'secret')
        self.app.get('/profiles/update/1', status=200)

    def test_edit_save_ok(self):
        self.login('admin', 'secret')
        values = {
            "first_name":"Firstname",
            "last_name":"Lastname",
            "address":"",
            "birthday__month":"MM",
            "birthday__day":"DD",
            "birthday__year":"",
            "email":"mail@example.com",
            "url":"",
            "phone":""
        }
        self.app.post('/profiles/update/1', values, status=302)

if __name__ == '__main__':
    unittest.main()
