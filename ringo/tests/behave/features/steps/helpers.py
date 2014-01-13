def get_csrf_token(res):
    return res.forms[0].get('csrf_token').value

def get_modul_path(modul):
    path = []
    if modul in ["user", "users"]:
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
    elif modul == "comments":
        path.append("comments")
    elif modul == "tags":
        path.append("tags")
    elif modul == "todos":
        path.append("todos")
    return path
