from behave import *

from helpers import get_modul_path, get_csrf_token

@when(u'calls the overview web-url of modul {modul}')
def step_impl(context, modul):
    path = get_modul_path(modul)
    path.append("list")
    context.resp = context.app.get("/%s" % "/".join(path), status="*")

@when(u'calls the create web-url of modul {modul}')
def step_impl(context, modul):
    path = get_modul_path(modul)
    path.append("create")
    context.resp = context.app.get("/%s" % "/".join(path), status="*")

@when(u'calls the read web-url for item {id} of modul {modul}')
def step_impl(context, id, modul):
    path = get_modul_path(modul)
    path.append("read")
    path.append(str(id))
    context.resp = context.app.get("/%s" % "/".join(path), status="*")

@when(u'calls the edit web-url for item {id} of modul {modul}')
def step_impl(context, id, modul):
    path = get_modul_path(modul)
    path.append("update")
    path.append(str(id))
    context.resp = context.app.get("/%s" % "/".join(path), status="*")

@when(u'calls the delete web-url for item {id} of modul {modul}')
def step_impl(context, id, modul):
    path = get_modul_path(modul)
    path.append("delete")
    path.append(str(id))
    context.resp = context.app.get("/%s" % "/".join(path), status="*")

@when(u'confirms deletion for item {id} of modul {modul}')
def step_impl(context, id, modul):
    path = get_modul_path(modul)
    path.append("delete")
    path.append(str(id))
    csrf = get_csrf_token(context.resp)
    values = {
        "confirmed": "1",
        "csrf_token": csrf
    }
    context.resp = context.app.post("/%s" % "/".join(path), values)

@when(u'calls the export web-url for item {id} of modul {modul}')
def step_impl(context, id, modul):
    path = get_modul_path(modul)
    path.append("export")
    path.append(str(id))
    context.resp = context.app.get("/%s" % "/".join(path), status="*")

@when(u'calls the import web-url for modul {modul}')
def step_impl(context, modul):
    path = get_modul_path(modul)
    path.append("import")
    context.resp = context.app.get("/%s" % "/".join(path), status="*")
