from behave import *
from helpers import get_csrf_token, get_modul_path

@when(u'submits data ({error}) to create a item of modul todos')
def step_impl(context, error):
    path = get_modul_path("todos")
    path.append("create")
    csrf = get_csrf_token(context.resp)
    values = {
        "name": "Test",
        "priority": "1",
        "description": "Test description",
        "csrf_token": csrf
    }
    if error == "missing-field":
        values['name'] = ""
    if error == "conditional-required":
        values['reminder'] = "2"
    context.resp = context.app.post("/%s" % "/".join(path), values, status="*")

@when(u'submits data ({error}) to edit item {id} of modul todos')
def step_impl(context, error, id):
    path = get_modul_path("todos")
    path.append("update")
    path.append(str(id))
    csrf = get_csrf_token(context.resp)
    values = {
        "name": "Test",
        "priority": "1",
        "todo_state_id": "1",
        "description": "Test description",
        "csrf_token": csrf
    }
    if error == "missing-field":
        values['name'] = ""
    if error == "conditional-required":
        values['reminder'] = "2"
    context.resp = context.app.post("/%s" % "/".join(path), values, status="*")
