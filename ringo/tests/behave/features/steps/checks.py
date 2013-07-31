from behave import *

@then(u'the user should get a 200 http respone')
def step_impl(context):
    assert context.resp.status_int == 200
