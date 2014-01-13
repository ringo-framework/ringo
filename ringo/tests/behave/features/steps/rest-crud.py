from behave import *

from helpers import get_modul_path, get_csrf_token

@when(u'calls the overview rest-url of modul {modul}')
def step_impl(context, modul):
    path = get_modul_path(modul)
    context.resp = context.app.get("/rest/%s" % "/".join(path), status="*")

@when(u'calls the create rest-url of modul {modul}')
def step_impl(context, modul):
    path = get_modul_path(modul)
    context.resp = context.app.post("/rest/%s" % "/".join(path), {}, status="*")

@when(u'calls the read rest-url for item {id} of modul {modul}')
def step_impl(context, id, modul):
    path = get_modul_path(modul)
    path.append(str(id))
    context.resp = context.app.get("/rest/%s" % "/".join(path), status="*")

@when(u'calls the edit rest-url for item {id} of modul {modul}')
def step_impl(context, id, modul):
    path = get_modul_path(modul)
    path.append(str(id))
    context.resp = context.app.put("/rest/%s" % "/".join(path), {}, status="*")

@when(u'calls the delete rest-url for item {id} of modul {modul}')
def step_impl(context, id, modul):
    path = get_modul_path(modul)
    path.append(str(id))
    context.resp = context.app.delete("/rest/%s" % "/".join(path), status="*")
