from behave import *

from helpers import get_modul_path, get_csrf_token

@when(u'calls the overview rest-url of modul {modul}')
def step_impl(context, modul):
    path = get_modul_path(modul)
    context.resp = context.app.get("/rest/%s" % "/".join(path), status="*")

#@when(u'calls the create rest-url of modul {modul}')
#def step_impl(context, modul):
#    path = get_modul_path(modul)
#    path.append("create")
#    context.resp = context.app.get("/rest/%s" % "/".join(path), status="*")

@when(u'calls the read rest-url for item {id} of modul {modul}')
def step_impl(context, id, modul):
    path = get_modul_path(modul)
    path.append(str(id))
    context.resp = context.app.get("/rest/%s" % "/".join(path), status="*")

#@when(u'calls the edit rest-url for item {id} of modul {modul}')
#def step_impl(context, id, modul):
#    path = get_modul_path(modul)
#    path.append("update")
#    path.append(str(id))
#    context.resp = context.app.get("/rest/%s" % "/".join(path), status="*")

#@when(u'calls the delete rest-url for item {id} of modul {modul}')
#def step_impl(context, id, modul):
#    path = get_modul_path(modul)
#    path.append("delete")
#    path.append(str(id))
#    context.resp = context.app.get("/rest/%s" % "/".join(path), status="*")

#@when(u'confirms deletion for item {id} of modul {modul}')
#def step_impl(context, id, modul):
#    path = get_modul_path(modul)
#    path.append("delete")
#    path.append(str(id))
#    csrf = get_csrf_token(context.resp)
#    values = {
#        "confirmed": "1",
#        "csrf_token": csrf
#    }
#    context.resp = context.app.post("/%s" % "/".join(path), values)
