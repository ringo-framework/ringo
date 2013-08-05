from behave import *

def login(context, username, password):
    '''Will login the user with username and password. On default we we do
    a check on a successfull login'''
    logout(context)
    response = context.app.post('/auth/login',
        params={'login': username,
                'pass': password},
    )
    return response

def logout(context):
    'Logout the currently logged in user (if any)' 
    response = context.app.get('/auth/logout',
        params={}
    )
    return response

@given(u'a {role} user')
def step_impl(context, role):
    if role == "anonymous":
        assert (logout(context).status_int == 302)
    elif role == "admin":
        resp = login(context, "admin", "secret")
        assert (resp.status_int == 302)
    else:
        assert False
