from behave import *

def get_csrf_token(res):
    return res.form.get('csrf_token').value

@when(u'opens the login page')
def step_impl(context):
    response = context.app.get('/auth/login')
    assert (response.status_int == 200)

@when(u'submits valid login data')
def step_impl(context):
    response = context.app.get('/auth/login')
    csrf = get_csrf_token(response)
    response = context.app.post('/auth/login',
        params={'login': 'admin',
                'pass': 'secret',
                'csrf_token': csrf},
    )
    context.resp = response

@when(u'submits invalid login data')
def step_impl(context):
    csrf = get_csrf_token(response)
    response = context.app.post('/auth/login',
        params={'login': 'admin',
                'pass': 'secret2',
                'csrf_token': csrf},
    )
    context.resp = response

@when(u'opens the registration page')
def step_impl(context):
    response = context.app.get('/auth/register_user')
    assert (response.status_int == 200)

@when(u'submits valid registration data')
def step_impl(context):
    response = context.app.get('/auth/register_user')
    csrf = get_csrf_token(response)
    response = context.app.post('/auth/register_user',
        params={'login': 'testuser',
                'pass': 'mypass',
                'pass2': 'mypass',
                'csrf_token': csrf,
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
    response = context.app.get('/auth/forgot_password')
    csrf = get_csrf_token(response)
    response = context.app.post('/auth/forgot_password',
        params={'login': 'admin', 'csrf_token': csrf},
    )
    context.resp = response

@when(u'submits invalid userdata data')
def step_impl(context):
    response = context.app.get('/auth/forgot_password')
    csrf = get_csrf_token(response)
    response = context.app.post('/auth/forgot_password',
        params={'login': 'unknowuser', 'csrf_token': csrf},
    )
    context.resp = response

