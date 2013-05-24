# -*- coding:utf-8 -*-
#!/usr/bin/env python
# Authors:
# Torsten Irländer <torsten.irlaender@intevation.de>

import sys
import os
import logging
import transaction
import pkg_resources
import argparse
import ConfigParser, os

from ringo  import modul_template_dir
from ringo.lib.i18n import _
from ringo.model import DBSession
from ringo.model.modul import ModulItem, _create_default_actions

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)
from sqlalchemy import engine_from_config

from mako.lookup import TemplateLookup

log = logging.getLogger(name=__name__)
template_lookup = TemplateLookup(directories=[modul_template_dir],
                                 module_directory='/tmp/ringo_modules')

MODEL = """
"""

VIEW = """
"""

def get_app_path(config_file):
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    egg = config.get('app:main', 'use')
    package = egg.split(':')[1]
    path = pkg_resources.get_distribution(package).location
    return path

def get_db(config_file):
    setup_logging(config_file)
    settings = get_appsettings(config_file)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    return DBSession

def add_db_entry(name, session):
    print 'Adding new entry in modules table for "%s"... ' % name,
    modul_name = name + "s"
    label = name.capitalize()
    label_plural = label + "s"
    try:
        return 6
        #with transaction.manager:
        #    modul = ModulItem(name=modul_name)
        #    modul.label = _(label)
        #    modul.label_plural = _(label_plural)
        #    modul.actions.extend(_create_default_actions(session))
        #    session.add(modul)
        #    session.flush()
        #print 'Ok.'
        ## Get last inserted id.
        #last_modul = session.query(ModulItem).filter(ModulItem.name == modul_name).one()
        #return last_modul.id
    except Exception, e:
        print e
        print 'Failed.'

def get_template(name):
    base_path = pkg_resources.get_distribution('ringo').location
    template_path = os.path.join(base_path, 'scripts', 'templates', name+".tmpl")
    print template_path


def add_model_file(id, name, path):
    target_file = os.path.join(path, 'ringo', 'model', '%s.py' % name)
    print 'Adding new model file "%s"... ' % target_file,
    template = template_lookup.get_template("model.mako")
    try:
        clazzname = name.capitalize()
        tablename = name+'s'
        values = {
            'table': tablename,
            'id': id,
            'clazz': clazzname
        }
        template = template_lookup.get_template("model.mako")
        generated = template.render(**values)
        outfile = open(target_file, 'w+')
        outfile.write(generated)
        outfile.close()
        print 'Ok.'
    except Exception, e:
        print 'Failed.'

def add_view_file(name, path):
    target_file= os.path.join(path, 'views', '%s.py' % name)
    print 'Adding new view file "%s"... ' % target_file,
    try:
        print 'Ok.'
    except:
        print 'Failed.'

def add_routes(name, path):
    target_file = os.path.join(path, '__init__.py')
    print 'Adding routes to "%s"... ' % target_file,
    try:
        print 'Ok.'
    except:
        print 'Failed.'


def add_modul(name, path, config):
    print 'Adding modul "%s" under "%s"' % (name, path)
    # 1. Adding the new model to the database
    session = get_db(config)
    modul_id = add_db_entry(name, session)
    #print "Inserted modul with ID %s" % modul_id
    # 2. Adding a new model file.
    add_model_file(modul_id, name, path)
    # 3. Adding a new view file.
    add_view_file(name, path)
    # 4. Configure Routes for the new modul.
    add_routes(name, path)

def main():
    '''Main function'''
    parser = argparse.ArgumentParser(description='Adds a new modul to the application.')
    parser.add_argument('name', type=str, help='Name of the modul')
    parser.add_argument('--config', dest='configuration',
                        help='Configuration (ini) of the application', required=True)

    args = parser.parse_args()
    try:
        app_config = args.configuration
        app_path = get_app_path(app_config)
    except pkg_resources.DistributionNotFound:
        print 'Failed: Application "%s" was not found' % app_name
        return sys.exit(1)

    add_modul(args.name, app_path, app_config)

    return sys.exit(1)

if __name__ == '__main__':
    main()
