import pytest


def test_encrypt_default():
    from ringo.lib.security import encrypt_password, verify_password
    password = "secret"
    result = encrypt_password(password)
    assert verify_password(password, result)


def test_verify():
    from ringo.lib.security import verify_password
    plain_password = "secret"
    encrypt_password = "$pbkdf2-sha256$8760$1Nobo7T2HkOI0bpX6h2D0A$tOjUoYB8IzNuxonEedMeO88gkbSz/J7HjHFwNbQuR7o"
    assert verify_password(plain_password, encrypt_password)


def test_needs_update_true():
    from ringo.lib.security import passwords_needs_update
    password = "asdjfakjfaksdfkasdkfasdf"
    assert passwords_needs_update(password)


def test_needs_update_false():
    from ringo.lib.security import passwords_needs_update
    password = "$pbkdf2-sha256$8760$1Nobo7T2HkOI0bpX6h2D0A$tOjUoYB8IzNuxonEedMeO88gkbSz/J7HjHFwNbQuR7o"
    assert not passwords_needs_update(password)


def test_login_ok():
    from ringo.lib.security import login
    username = "admin"
    password = "secret"
    assert login(username, password) != None


def test_login_fail():
    from ringo.lib.security import login
    username = "admin"
    password = "worngpassword"
    assert login(username, password) == None


@pytest.fixture()
def modulrequest(apprequest):
    from ringo.model.modul import ModulItem
    item = apprequest.db.query(ModulItem).filter(ModulItem.id == 1).one()
    apprequest.context.item = item
    apprequest.matchdict = {'id': 1}
    apprequest.session['modules.1.form.page'] = 2
    return apprequest


def test_diff_equal(modulrequest):
    from ringo.lib.security import ValueChecker
    checker = ValueChecker()
    values = modulrequest.context.item.get_values(include_relations=True)
    assert len(checker._diff(values, values)) == 0


def test_diff_removed_one(modulrequest):
    from ringo.lib.security import ValueChecker
    checker = ValueChecker()
    values = modulrequest.context.item.get_values(include_relations=True)['actions']
    values2 = values[0:-1]
    assert len(checker._diff(values, values2)) == 1
    assert checker._diff(values, values2)[0][1] == -1


def test_diff_removed_one2(modulrequest):
    from ringo.model.modul import ActionItem
    from ringo.lib.security import ValueChecker
    action = modulrequest.db.query(ActionItem).filter(ActionItem.id == 20).one()
    checker = ValueChecker()
    values = modulrequest.context.item.get_values(include_relations=True)['actions']
    values2 = values[::]
    values2.append(action)
    assert len(checker._diff(values, values2)) == 1
    assert checker._diff(values, values2)[0][1] == 1


def test_empty_values(modulrequest):
    """No values provided. So no checks are actually done."""
    from ringo.lib.security import ValueChecker
    checker = ValueChecker()
    checker.check(modulrequest.context.item.__class__, {}, modulrequest, modulrequest.context.item)


def test_equal_values(modulrequest):
    from ringo.lib.security import ValueChecker
    checker = ValueChecker()
    values = modulrequest.context.item.get_values(include_relations=True)
    checker.check(modulrequest.context.item.__class__, values, modulrequest, modulrequest.context.item)
