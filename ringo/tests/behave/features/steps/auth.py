from behave import *

@when(u'opens the login page')
def step_impl(context):
    response = context.app.get('/auth/login')
    assert (response.status_int == 200)

@when(u'submits valid login data')
def step_impl(context):
    response = context.app.post('/auth/login',
        params={'login': 'admin',
                'pass': 'secret'},
    )
    context.resp = response

@when(u'submits invalid login data')
def step_impl(context):
    response = context.app.post('/auth/login',
        params={'login': 'admin',
                'pass': 'wrongpassword'},
    )
    context.resp = response

@when(u'opens the registration page')
def step_impl(context):
    response = context.app.get('/auth/register_user')
    assert (response.status_int == 200)

@when(u'submits valid registration data')
def step_impl(context):
    response = context.app.post('/auth/register_user',
        params={'login': 'testuser',
                'pass': 'mypass',
                'pass2': 'mypass',
                'email': 'testuser@example.com',
        },
    )
    context.resp = response

@when(u'opens the password reminder page')
def step_impl(context):
    response = context.app.get('/auth/forgot_password')
    assert (response.status_int == 200)

@when(u'submits valid userdata data')
def step_impl(context):
    response = context.app.post('/auth/forgot_password',
        params={'login': 'admin'},
    )
    context.resp = response

@when(u'submits invalid userdata data')
def step_impl(context):
    response = context.app.post('/auth/forgot_password',
        params={'login': 'unknowuser'},
    )
    context.resp = response

