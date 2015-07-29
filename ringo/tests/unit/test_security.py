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

class ValueErrorTests(BaseUnitTest):

    def setUp(self):
        super(ValueErrorTests, self).setUp()
        from ringo.model.modul import ModulItem
        item = self.request.db.query(ModulItem).filter(ModulItem.id == 1).one()
        self.request.context.item = item
        self.request.matchdict = {'id': 1}
        self.request.session['modules.1.form.page'] = 2

    def test_diff_equal(self):
        from ringo.lib.security import ValueChecker
        checker = ValueChecker()
        values = self.request.context.item.get_values(include_relations=True)
        self.assertTrue(len(checker._diff(values, values)) == 0)

    def test_diff_removed_one(self):
        from ringo.lib.security import ValueChecker
        checker = ValueChecker()
        values = self.request.context.item.get_values(include_relations=True)['actions']
        values2 = values[0:-1]
        self.assertTrue(len(checker._diff(values, values2)) == 1)
        self.assertTrue(checker._diff(values, values2)[0][1] == -1)

    def test_diff_removed_one(self):
        from ringo.model.modul import ActionItem
        from ringo.lib.security import ValueChecker
        action = self.request.db.query(ActionItem).filter(ActionItem.id == 20).one()
        checker = ValueChecker()
        values = self.request.context.item.get_values(include_relations=True)['actions']
        values2 = values[::]
        values2.append(action)
        self.assertTrue(len(checker._diff(values, values2)) == 1)
        self.assertTrue(checker._diff(values, values2)[0][1] == 1)

    def test_empty_values(self):
        """No values provided. So no checks are actually done."""
        from ringo.lib.security import ValueChecker
        checker = ValueChecker()
        checker.check(self.request.context.item.__class__, {}, self.request, self.request.context.item)

    def test_equal_values(self):
        from ringo.lib.security import ValueChecker
        checker = ValueChecker()
        values = self.request.context.item.get_values(include_relations=True)
        checker.check(self.request.context.item.__class__, values, self.request, self.request.context.item)


if __name__ == '__main__':
    unittest.main()
