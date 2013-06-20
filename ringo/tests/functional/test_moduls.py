import unittest
from sqlalchemy.orm.exc import NoResultFound
from ringo.model.modul import ModulItem
from ringo.tests import BaseFunctionalTest

class TestModulItem(BaseFunctionalTest):

    def test_wrong_url(self):
        self.login('admin', 'secret')
        self.app.get('/modules/listtest', status=404)

    def test_list(self):
        self.login('admin', 'secret')
        self.app.get('/modules/list', status=200)

    def test_read(self):
        self.login('admin', 'secret')
        self.app.get('/modules/read/1', status=200)

    def test_read_unknown(self):
        self.login('admin', 'secret')
        try:
            self.app.get('/modules/read/1234')
        except NoResultFound:
            return True
        # Must fail!
        self.assertEqual(0,1)

    def test_edit(self):
        self.login('admin', 'secret')
        self.app.get('/modules/update/1', status=200)

    # TODO: Not sure how to craft a POST request. This request seems to
    # loose actions which causes routing errors later.
    #def test_edit_save_ok(self):
    #    self.login('admin', 'secret')
    #    values = {
    #        "name":"modules",
    #        "label":"Modul",
    #        "label_plural":"Modules",
    #        "description":"",
    #        "str_repr":"",
    #        "actions":["1", "2", "3"],
    #    }
    #    self.app.post('/modules/update/1', values, status=302)

if __name__ == '__main__':
    unittest.main()
