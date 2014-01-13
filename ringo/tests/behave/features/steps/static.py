from behave import *

from helpers import get_modul_path, get_csrf_token

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

