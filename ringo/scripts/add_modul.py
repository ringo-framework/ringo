# -*- coding:utf-8 -*-
#!/usr/bin/env python
# Authors:
# Torsten Irlaender <torsten.irlaender@intevation.de>

import sys
import os
import logging
import transaction
import pkg_resources
import argparse
import ConfigParser
from tempfile import mkstemp
from shutil import move
from ringo import modul_template_dir
from ringo.lib.sql import DBSession
from ringo.model import Base
from ringo.model.modul import ModulItem, ActionItem

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)
from sqlalchemy import engine_from_config

from mako.lookup import TemplateLookup

log = logging.getLogger(name=__name__)
template_lookup = TemplateLookup(directories=[modul_template_dir])

MODEL = """
"""

VIEW = """
"""

def _create_default_actions(dbsession, ignore=[]):
    # TODO: Translate the name of the Action (torsten) <2013-07-10 09:32>
    a0 = ActionItem(name="List", url="list", icon="icon-list-alt")
    a1 = ActionItem(name="Create", url="create", icon=" icon-plus")
    a2 = ActionItem(name="Read", url="read/{id}", icon="icon-eye-open")
    a3 = ActionItem(name="Update", url="update/{id}", icon="icon-edit")
    a4 = ActionItem(name="Delete", url="delete/{id}", icon="icon-trash")
    a5 = ActionItem(name="Import", url="import", icon="icon-import")
    a6 = ActionItem(name="Export", url="export/{id}", icon="icon-export")
    actions = []
    if not "list" in ignore:
        dbsession.add(a0)
        actions.append(a0)
    if not "create" in ignore:
        dbsession.add(a1)
        actions.append(a1)
    if not "read" in ignore:
        dbsession.add(a2)
        actions.append(a2)
    if not "update" in ignore:
        dbsession.add(a3)
        actions.append(a3)
    if not "delete" in ignore:
        dbsession.add(a4)
        actions.append(a4)
    if not "import" in ignore:
        dbsession.add(a5)
        actions.append(a5)
    if not "export" in ignore:
        dbsession.add(a6)
        actions.append(a6)
    return actions


def my_import(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def get_package_name(config_file):
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    egg = config.get('app:main', 'use')
    package = egg.split(':')[1]
    return package


def get_app_path(package):
    path = pkg_resources.get_distribution(package).location
    return path


def get_engine(config_file):
    setup_logging(config_file)
    settings = get_appsettings(config_file)
    engine = engine_from_config(settings, 'sqlalchemy.')
    return engine


def add_db_entry(package, name, engine):
    print 'Adding new entry in modules table for "%s"... ' % name,
    DBSession.configure(bind=engine)
    modul_name = name + "s"
    label = name.capitalize()
    label_plural = label + "s"
    clazzpath = ".".join([package, 'model', name, label])
    try:
        with transaction.manager:
            modul = ModulItem(name=modul_name)
            modul.clazzpath = clazzpath
            modul.label = label
            modul.label_plural = label_plural
            modul.display = "header-menu"
            modul.str_repr = "%%s|id"
            modul.actions.extend(_create_default_actions(DBSession))
            DBSession.add(modul)
            DBSession.flush()
        # Get last inserted id.
        last_modul = DBSession.query(ModulItem).filter(ModulItem.name == modul_name).one()
        print 'Ok.'
        return last_modul.id
    except Exception, e:
        print e
        print 'Failed.'


def add_model_file(package, modul, id, clazz):
    target_file = os.path.join(get_app_path(package), package, 'model', '%s.py' % modul)
    print 'Adding new model file "%s"... ' % target_file,
    try:
        tablename = modul + 's'
        label = modul.capitalize()
        label_plural = label + "s"
        clazzpath = ".".join([package, 'model', modul, label])
        values = {
            'modul': modul,
            'clazzpath': clazzpath,
            'label': label,
            'label_plural': label_plural,
            'modul': modul,
            'table': tablename,
            'id': id,
            'clazz': clazz
        }
        template = template_lookup.get_template("model.mako")
        generated = template.render(**values)
        outfile = open(target_file, 'w+')
        outfile.write(generated)
        outfile.close()
        print 'Ok.'
    except Exception:
        print 'Failed.'


def add_view_file(package, modul, clazz):
    filename = modul + "s"
    target_file= os.path.join(get_app_path(package), package, 'views', '%s.py' % filename)
    print 'Adding new view file "%s"... ' % target_file,
    try:
        values = {
            'package': package,
            'modul': modul,
            'clazz': clazz
        }
        template = template_lookup.get_template("view.mako")
        generated = template.render(**values)
        outfile = open(target_file, 'w+')
        outfile.write(generated)
        outfile.close()
        print 'Ok.'
    except:
        print 'Failed.'


def add_form_file(package, modul):
    filename = modul + "s"
    target_file= os.path.join(get_app_path(package), package, 'views', 'forms', '%s.xml' % filename)
    print 'Adding new form configuration file "%s"... ' % target_file,
    try:
        values = {}
        template = template_lookup.get_template("form.mako")
        generated = template.render(**values)
        outfile = open(target_file, 'w+')
        outfile.write(generated)
        outfile.close()
        print 'Ok.'
    except:
        print 'Failed.'


def add_table_file(package, modul):
    filename = modul + "s"
    target_file= os.path.join(get_app_path(package), package, 'views', 'tables', '%s.json' % filename)
    print 'Adding new table configuration file "%s"... ' % target_file,
    try:
        values = {}
        template = template_lookup.get_template("table.json")
        generated = template.render(**values)
        outfile = open(target_file, 'w+')
        outfile.write(generated)
        outfile.close()
        print 'Ok.'
    except:
        print 'Failed.'


def add_routes(package, modul, clazz):
    target_file = os.path.join(get_app_path(package), package, '__init__.py')
    print 'Adding routes to "%s"... ' % target_file,
    try:
        importstr = "from %s.model.%s import %s\n# AUTOREPLACEIMPORT" % (package, modul, clazz)
        routestr = "add_route(config, %s)\n    # AUTOREPLACEROUTE" % (clazz)
        replace(target_file, '# AUTOREPLACEIMPORT', importstr)
        replace(target_file, '# AUTOREPLACEROUTE', routestr)
        print 'Ok.'
    except:
        print 'Failed.'


def replace(file_path, pattern, subst):
    #Create temp file
    fh, abs_path = mkstemp()
    new_file = open(abs_path, 'w')
    old_file = open(file_path)
    for line in old_file:
        new_file.write(line.replace(pattern, subst))
    #close temp file
    new_file.close()
    os.close(fh)
    old_file.close()
    #Remove original file
    os.remove(file_path)
    #Move new file
    move(abs_path, file_path)


def add_modul(name, package, config):
    path = get_app_path(package)
    print 'Adding modul "%s" under "%s"' % (name, path)

    modul = name
    clazz = name.capitalize()

    # 1. Adding the new model to the database
    engine = get_engine(config)
    modul_id = add_db_entry(package, modul, engine)
    #print "Inserted modul with ID %s" % modul_id
    # 2. Adding a new model file.
    add_model_file(package, modul, modul_id, clazz)
    # 3. Adding a new view file.
    add_view_file(package, modul, clazz)
    # 4. Adding a new form and table configuration
    add_form_file(package, modul)
    add_table_file(package, modul)
    # 5. Configure Routes for the new modul.
    add_routes(package, modul, clazz)

    # 7. Dynamic import of new clazz to be able to create the table.
    mod = __import__('%s.model.%s' % (package, modul), fromlist=[clazz])
    klass = getattr(mod, clazz)
    Base.metadata.create_all(engine)


def main():
    '''Main function'''
    parser = argparse.ArgumentParser(description='Adds a new modul to the application.')
    parser.add_argument('name', type=str, help='Name of the modul')
    parser.add_argument('--config', dest='configuration',
                        help='Configuration (ini) of the application', required=True)

    args = parser.parse_args()
    try:
        app_config = args.configuration
        package = get_package_name(app_config)
    except pkg_resources.DistributionNotFound:
        print 'Failed: Application "%s" was not found' % app_name
        return sys.exit(1)

    add_modul(args.name, package, app_config)

    return sys.exit(1)

if __name__ == '__main__':
    main()
