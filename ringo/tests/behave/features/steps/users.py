from behave import *
from helpers import get_csrf_token, get_modul_path

@when(u'submits data ({error}) to create a item of modul users')
def step_impl(context, error):
    path = get_modul_path("users")
    path.append("create")
    csrf = get_csrf_token(context.resp)
    values = {
        "login": "test",
        "_first_name": "xxx",
        "_last_name": "yyy",
        "_email": "test@test.de",
        "password": "0123456789abc",
        "_retype_password": "0123456789abc",
        "csrf_token": csrf
    }
    if error == "password-missmatch":
        values['_retype_password'] = "test2"
    if error == "missing-login":
        values['login'] = ""
    context.resp = context.app.post("/%s" % "/".join(path), values, status="*")

@when(u'submits data ({error}) to edit item {id} of modul users')
def step_impl(context, error, id):
    path = get_modul_path("users")
    path.append("update")
    path.append(str(id))
    csrf = get_csrf_token(context.resp)
    values = {
        "id": id,
        "login": "test2",
        "_first_name": "xxx",
        "_last_name": "yyy",
        "_email": "test@test.de",
        "password": "0123456789abc",
        "_retype_password": "0123456789abc",
        "csrf_token": csrf
    }
    if error == "missing-login":
        values['login'] = ""
    context.resp = context.app.post("/%s" % "/".join(path), values, status="*")
