import os
import coverage
from paste.deploy.loadwsgi import appconfig
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker

from ringo import main
from webtest import TestApp

cov = coverage.coverage()

def get_settings():
    here = os.path.dirname(__file__)
    settings = appconfig('config:' + os.path.join(here, '../../../../', 'test.ini'))
    return settings

def before_all(context):
    cov.start()
    context.engine = engine_from_config(get_settings(), prefix='sqlalchemy.')
    context.Session = sessionmaker()

def before_feature(context, feature):
    settings = get_settings()
    context.app = TestApp(main({}, **settings))

def after_all(context):
    cov.stop()
    cov.save()
    #cov.html_report()
