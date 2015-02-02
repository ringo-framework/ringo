from behave import *

@then(u'the user should get a {response} http response')
def step_impl(context, response):
    ok = (context.resp.status_int == int(response))
    if ok:
        assert True
    else:
        assert False
