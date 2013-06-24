import unittest
from ringo.tests import BaseFunctionalTest
from ringo.tests.functional.test_users import TestUser


class TestAuth(BaseFunctionalTest):

    def test_403(self):
        self.app.get('/users/list', status=403)

    def test_login(self):
        self.app.get('/auth/login', status=200)

    def test_login_ok(self):
        self.logout()
        values = {'login': 'admin', 'pass': 'secret'}
        self.app.post('/auth/login', values, status=302)

    def test_login_fail(self):
        self.logout()
        values = {'login': 'admin', 'pass': 'secret2'}
        self.app.post('/auth/login', values, status=200)

    def test_logout(self):
        self.app.get('/auth/logout', status=302)

    def test_register(self):
        self.app.get('/auth/register_user', status=200)

    def test_register_fail(self):
        values = {
            'login': 'admin',
            'pass': '12345678',
            'pass2': '12345678',
            'email': 'test@example.com'
        }
        self.app.post('/auth/register_user', values, status=200)

    def test_register_ok(self):
        values = {
            'login': 'newuser',
            'pass': '12345678',
            'pass2': '12345678',
            'email': 'test@example.com'
        }
        self.app.post('/auth/register_user', values, status=302)

    def test_forgot(self):
        self.app.get('/auth/forgot_password', status=200)

    def test_forgot_fail(self):
        values = {
            'login': 'xxx'
        }
        # Note that the response is the same as on success here as we do
        # not want to provide any information if ther is a user with
        # this login.
        response = self.app.post('/auth/forgot_password', values, status=302).follow()
        assert 'Password reset token has been sent' in response

    def test_forgot_ok(self):
        values = {
            'login': 'admin'
        }
        response = self.app.post('/auth/forgot_password', values, status=302).follow()
        assert 'Password reset token has been sent' in response

    def test_confirm_ok(self):
        response = self.app.get('/auth/confirm_user/0e3cc848-22f6-4ff7-a562-12baf3037439', status=200)
        assert 'The user has beed successfull confirmed.' in response

    def test_confirm_fail(self):
        response = self.app.get('/auth/confirm_user/xxx', status=200)
        assert 'The user was not confirmed' in response

    # Token is already reseted on confirmation. So this test will fail.
    # def test_reset_ok(self):
    #    self.login('admin', 'secret')
    #    values = {
    #            'login': 'admin',
    #            'groups': '1',
    #            'gid': '',
    #            'activated': 'True',
    #            'activation_token': '0e3cc848-22f6-4ff7-a562-12baf3037439'
    #    }
    #    self.app.post('/users/update/1', values, status=302)
    #    response = self.app.get('/auth/reset_password/0e3cc848-22f6-4ff7-a562-12baf3037439', status=200)
    #    assert 'Password has been successfull resetted' in response

    def test_reset_fail(self):
        response = self.app.get('/auth/reset_password/xxx', status=200)
        assert 'Password was not resetted' in response

if __name__ == '__main__':
    unittest.main()
