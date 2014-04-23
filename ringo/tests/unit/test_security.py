import unittest
from ringo.tests import BaseUnitTest


class PasswordTests(BaseUnitTest):

    def test_encrypt_default(self):
        from ringo.lib.security import encrypt_password, verify_password
        password = "secret"
        result = encrypt_password(password)
        self.assertTrue(verify_password(password, result))

    def test_verify(self):
        from ringo.lib.security import verify_password
        plain_password = "secret"
        encrypt_password = "$pbkdf2-sha256$8760$1Nobo7T2HkOI0bpX6h2D0A$tOjUoYB8IzNuxonEedMeO88gkbSz/J7HjHFwNbQuR7o"
        self.assertTrue(verify_password(plain_password, encrypt_password))

    def test_needs_update_true(self):
        from ringo.lib.security import passwords_needs_update
        password = "asdjfakjfaksdfkasdkfasdf"
        self.assertTrue(passwords_needs_update(password))

    def test_needs_update_false(self):
        from ringo.lib.security import passwords_needs_update
        password = "$pbkdf2-sha256$8760$1Nobo7T2HkOI0bpX6h2D0A$tOjUoYB8IzNuxonEedMeO88gkbSz/J7HjHFwNbQuR7o"
        self.assertFalse(passwords_needs_update(password))

    def test_login_ok(self):
        from ringo.lib.security import login
        username = "admin"
        password = "secret"
        self.assertNotEqual(login(username, password), None)

    def test_login_fail(self):
        from ringo.lib.security import login
        username = "admin"
        password = "worngpassword"
        self.assertEqual(login(username, password), None)

if __name__ == '__main__':
    unittest.main()
