import os
import subprocess
import uuid
import transaction
import pkg_resources
from sqlalchemy import func
from mako.lookup import TemplateLookup
from ringo.lib.helpers import get_app_location, dynamic_import
from ringo.scripts.db import (
    get_session, create_new_revision,
    handle_db_upgrade_command, replace_insert_stmt
)
from ringo.model.modul import ModulItem, ActionItem

# Directory with templates to generate views and models
base_dir = pkg_resources.get_distribution("ringo").location
modul_template_dir = os.path.join(base_dir, 'ringo', 'scripts', 'templates')
template_lookup = TemplateLookup(directories=[modul_template_dir])

mixinmap = {
    'owned': 'Owned',
    'meta': 'Meta',
    'state': 'StateMixin',
    'blobform': 'Blobform',
    'versioned': 'Versioned',
    'nested': 'Nested'
}


def _get_default_actions_sql(session, mid, action_id, ignore=[]):
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
            icon = "icon-edit"
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
                   """(id, mid, name, url, icon, uuid, bundle) """
                   """VALUES (%s, %s, '%s', '%s', '%s', '%s', '%s')""" %
                   (action_id, mid, name, url, icon, myuuid, bundle))
        action_id += 1
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

def get_next_actionid(session):
    id = session.query(func.max(ActionItem.id)).one()[0]
    return id + 1


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
    action_id = get_next_actionid(session)

    sql = []
    sql.append("""INSERT INTO "modules" """
               """VALUES (%s,'%s','%s','%s','%s', """
               """NULL, '%s','%s','%s', NULL)"""
               % (id, modul_name, clazzpath, label,
                  label_plural, str_repr, location, myuuid))
    sql.extend(_get_default_actions_sql(session, id, action_id))
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
        # Import the new model file. This is needed to be able to
        # generate the migration script properly.
        dynamic_import(clazzpath)
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
    """Will print generated SA fields ready to be pasted in the model
    based on the given form configuration.

    :args: command args
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

    print "\nGenerating fields for the %s model..." % args.name
    out = subprocess.check_output([
        "python",
        os.path.join(*formbar_path),
        "model",
        os.path.join(*path)
    ])
    print "\n", out


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
    path = create_new_revision(args, msg)
    replace_insert_stmt(path, sql)
    #print "Touching"
    #subprocess.call(["touch", path])
    #print "Finished Touching"
