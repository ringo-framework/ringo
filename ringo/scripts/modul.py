import os
import subprocess
import uuid
import transaction
from sqlalchemy import func
from mako.lookup import TemplateLookup
from ringo.config import modul_template_dir
from ringo.lib.helpers import get_app_location
from ringo.scripts.db import (
    get_session, create_new_revision,
    handle_db_upgrade_command
)
from ringo.model.modul import ModulItem
template_lookup = TemplateLookup(directories=[modul_template_dir])

mixinmap = {
    'owned': 'Owned',
    'meta': 'Meta',
    'logged': 'Logged',
    'state': 'StateMixin',
    'blobform': 'Blobform',
    'versioned': 'Versioned',
    'printable': 'Printable',
    'nested': 'Nested',
    'commented': 'Commented',
    'tagged': 'Tagged',
    'todo': 'Todo'
}


def _get_default_actions_sql(session, mid, ignore=[]):
    # TODO: Translate the name of the Action (torsten) <2013-07-10 09:32>
    sql = []
    for action in ['list', 'create', 'read', 'update',
                   'delete', 'import', 'export']:
        if action in ignore:
            continue
        myuuid = uuid.uuid4().hex
        if action == "list":
            name = "List"
            url = "list"
            icon = "icon-list-alt"
            bundle = 0
        if action == "create":
            name = "Create"
            url = "create"
            icon = "icon-plus"
            bundle = 0
        if action == "read":
            name = "Read"
            url = "read/{id}"
            icon = "icon-eye-open"
            bundle = 0
        if action == "update":
            name = "Update"
            url = "update/{id}"
            icon = "icon-eye-open"
            bundle = 0
        if action == "delete":
            name = "Delete"
            url = "delete/{id}"
            icon = "icon-eye-delete"
            bundle = 1
        if action == "import":
            name = "Import"
            url = "import"
            icon = "icon-import"
            bundle = 0
        if action == "export":
            name = "Export"
            url = "export/{id}"
            icon = "icon-export"
            bundle = 1

        sql.append("""INSERT INTO "actions" """
                   """(mid, name, url, icon, uuid, bundle) """
                   """VALUES (%s, '%s', '%s', '%s', '%s', '%s')""" %
                   (mid, name, url, icon, myuuid, bundle))
    return sql


def remove_db_entry(name, session):
    print 'Remove entry in modules table for "%s"... ' % name,
    modul_name = name + "s"
    try:
        with transaction.manager:
            session.query(ModulItem).filter(
                ModulItem.name == modul_name).delete()
            session.flush()
        # Get last inserted id.
        print 'Ok.'
    except Exception, e:
        print e
        print 'Failed.'


def get_next_modulid(package, session):
    if package == "ringo":
        id = session.query(
            func.max(ModulItem.id)).filter(ModulItem.id < 1000).one()[0]
    else:
        id = session.query(
            func.max(ModulItem.id)).filter(ModulItem.id > 999).one()[0]
    print id
    if id:
        return id + 1
    else:
        return 1000


def get_insert_statements(package, name, session):
    """Will retunr the INSERT statements for the new modul. They can be
    used in the migration scripts.

    :package: @todo
    :name: @todo
    :session: @todo
    :returns: @todo

    """
    modul_name = name + "s"
    label = name.capitalize()
    label_plural = label + "s"
    clazzpath = ".".join([package, 'model', name, label])
    location = "header-menu"
    str_repr = "%s|id"
    myuuid = uuid.uuid4().hex
    id = get_next_modulid(package, session)

    sql = []
    sql.append("""INSERT INTO "modules" """
               """VALUES (%s,'%s','%s','%s','%s', """
               """NULL, '%s','%s','%s', NULL); """
               % (id, modul_name, clazzpath, label,
                  label_plural, str_repr, location, myuuid))
    sql.extend(_get_default_actions_sql(session, id))
    return sql


def del_model_file(package, modul):
    target_file = os.path.join(get_app_location(package),
                               package, 'model', '%s.py' % modul)
    print 'Deleting model file "%s"... ' % target_file,
    try:
        os.remove(target_file)
        print 'Ok.'
    except Exception:
        print 'Failed.'


def add_model_file(package, modul, id, clazz, mixins):
    target_file = os.path.join(get_app_location(package),
                               package, 'model', '%s.py' % modul)
    print 'Adding new model file "%s"... ' % target_file,
    # Build mixins
    mixinclasses = []
    for mixin in mixins:
        mixinclasses.append(mixinmap[mixin])
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
            'clazz': clazz,
            'mixins': mixinclasses
        }
        template = template_lookup.get_template("model.mako")
        generated = template.render(**values)
        outfile = open(target_file, 'w+')
        outfile.write(generated)
        outfile.close()
        print 'Ok.'
    except Exception:
        print 'Failed.'


def del_form_file(package, modul):
    filename = modul + "s"
    target_file = os.path.join(get_app_location(package),
                               package, 'views', 'forms', '%s.xml' % filename)
    print 'Deleting form configuration file "%s"... ' % target_file,
    try:
        os.remove(target_file)
        print 'Ok.'
    except:
        print 'Failed.'


def add_form_file(package, modul):
    filename = modul + "s"
    target_file = os.path.join(get_app_location(package),
                               package, 'views', 'forms', '%s.xml' % filename)
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


def del_table_file(package, modul):
    filename = modul + "s"
    target_file = os.path.join(get_app_location(package),
                               package,
                               'views', 'tables', '%s.json' % filename)
    print 'Deleting table configuration file "%s"... ' % target_file,
    try:
        os.remove(target_file)
        print 'Ok.'
    except:
        print 'Failed.'


def add_table_file(package, modul):
    filename = modul + "s"
    target_file = os.path.join(get_app_location(package),
                               package,
                               'views', 'tables', '%s.json' % filename)
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


def handle_modul_fields_command(args):
    """@todo: Docstring for add_modul_add_command.

    :args: @todo
    :returns: @todo
    """
    path = []
    path.append(get_app_location(args.app))
    path.append(args.app)
    path.append("views")
    path.append("forms")
    path.append("%s.xml" % args.name)

    formbar_path = []
    formbar_path.append(get_app_location("formbar"))
    formbar_path.append("contrib")
    formbar_path.append("generate.py")
    print os.path.join(*formbar_path)

    print subprocess.check_output([
        "python",
        os.path.join(*formbar_path),
        "model",
        os.path.join(*path)
    ])


def handle_modul_delete_command(args):
    """@todo: Docstring for add_modul_add_command.

    :args: @todo
    :returns: @todo
    """
    path = []
    path.append(get_app_location(args.app))
    path.append(args.config)

    session = get_session(os.path.join(*path))
    package = args.app
    name = args.name
    remove_db_entry(name, session)
    del_model_file(package, name)
    del_form_file(package, name)
    del_table_file(package, name)


def handle_modul_add_command(args):
    """@todo: Docstring for add_modul_add_command.

    :args: @todo
    :returns: @todo
    """
    path = []
    path.append(get_app_location(args.app))
    path.append(args.config)

    session = get_session(os.path.join(*path))
    package = args.app
    name = args.name
    clazz = name.capitalize()
    modul_id = get_next_modulid(package, session)
    sql = get_insert_statements(package, name, session)
    add_model_file(package, name, modul_id, clazz, args.mixin)
    add_form_file(package, name)
    add_table_file(package, name)
    msg = "Added %s modul" % name
    create_new_revision(args, sql, msg)
    handle_db_upgrade_command(args)
