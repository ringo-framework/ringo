import unittest
from ringo.tests import BaseFunctionalTest

class TestRole(BaseFunctionalTest):

    def test_about(self):
        self.app.get('/about', status=200)

    def test_contact(self):
        self.app.get('/contact', status=200)

    def test_version(self):
        self.app.get('/version', status=200)

    def test_home(self):
        self.app.get('/', status=200)

if __name__ == '__main__':
    unittest.main()
