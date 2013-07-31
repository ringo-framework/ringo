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

def logout(contex):
    'Logout the currently logged in user (if any)' 
    response = context.app.get('/auth/logout',
        params={}
    )
    return response

@given(u'a anonymous user')
def step_impl(context):
    assert True
