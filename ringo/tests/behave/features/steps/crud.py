from behave import *


@when(u'opens the about page')
def step_impl(context):
    context.resp = context.app.get('/about')


@when(u'opens the contact page')
def step_impl(context):
    context.resp = context.app.get('/contact')


@when(u'opens the version page')
def step_impl(context):
    context.resp = context.app.get('/version')


@when(u'opens the home page')
def step_impl(context):
    context.resp = context.app.get('/')

def get_modul_path(modul):
    path = []
    if modul == "user":
        path.append("users")
    elif modul == "usergroup":
        path.append("usergroups")
    elif modul == "role":
        path.append("roles")
    elif modul == "profil":
        path.append("profiles")
    elif modul == "modul":
        path.append("modules")
    elif modul == "appointment":
        path.append("appointments")
    elif modul == "file":
        path.append("files")
    elif modul == "news":
        path.append("news")
    return path

@when(u'opens the create page of modul {modul}')
def step_impl(context, modul):
    path = get_modul_path(modul)
    path.append("create")
    context.resp = context.app.get("/%s" % "/".join(path), status="*")

@when(u'opens the read page for item {id} of modul {modul}')
def step_impl(context, id, modul):
    path = get_modul_path(modul)
    path.append("read")
    path.append(str(id))
    context.resp = context.app.get("/%s" % "/".join(path), status="*")

@when(u'opens the edit page for item {id} of modul {modul}')
def step_impl(context, id, modul):
    path = get_modul_path(modul)
    path.append("update")
    path.append(str(id))
    context.resp = context.app.get("/%s" % "/".join(path), status="*")

@when(u'deletes the item {id} of modul {modul}')
def step_impl(context, id, modul):
    path = get_modul_path(modul)
    path.append("delete")
    path.append(str(id))
    context.resp = context.app.get("/%s" % "/".join(path), status="*")
