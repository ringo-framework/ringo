import os
import fnmatch
import json
import subprocess
import uuid
import transaction
import pkg_resources
from sqlalchemy import func
from mako.lookup import TemplateLookup
from ringo.lib.helpers import get_app_location, dynamic_import
from ringo.scripts.db import (
    get_session, create_new_revision
)
from ringo.model.modul import ModulItem, ActionItem, ACTIONS

# Directory with templates to generate views and models
base_dir = pkg_resources.get_distribution("ringo").location
modul_template_dir = os.path.join(base_dir, 'ringo', 'scripts', 'templates')
template_lookup = TemplateLookup(directories=[modul_template_dir],
                                 default_filters=['h'])

mixinmap = {
    'owned': 'Owned',
    'meta': 'Meta',
    'state': 'StateMixin',
    'blobform': 'Blobform',
    'blob': 'Blob',
    'versioned': 'Versioned',
    'nested': 'Nested'
}


def get_modul_fixture(name, package, session):
    id = get_next_modulid(package, session)
    fixture = {}
    fixture["id"] = id
    fixture["name"] = name + "s"
    fixture["label"] = name.capitalize()
    fixture["label_plural"] = fixture["label"] + "s"
    fixture["clazzpath"] = ".".join([package, 'model',
                                     name, fixture["label"]])
    fixture["display"] = "header-menu"
    fixture["str_repr"] = "%s|id"
    fixture["uuid"] = str(uuid.uuid4())
    return fixture


def get_action_fixtures(session, mid, ignore=[]):
    # TODO: Translate the name of the Action (torsten) <2013-07-10 09:32>
    action_id = get_next_actionid(session)
    fixtures = []
    for key, action in ACTIONS.iteritems():
        if key in ignore:
            continue
        myuuid = str(uuid.uuid4())
        fixture = {}
        fixture["id"] = action_id
        fixture["uuid"] = myuuid
        fixture["mid"] = mid
        fixture["name"] = action.name
        fixture["url"] = action.url or ""
        fixture["icon"] = action.icon or ""
        fixture["bundle"] = action.bundle or False
        fixture["display"] = action.display or ""
        fixture["permission"] = action.permission or ""
        fixtures.append(fixture)
        action_id += 1
    return fixtures


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
    if id:
        return id + 1
    else:
        return 1000


def get_next_actionid(session):
    id = session.query(func.max(ActionItem.id)).one()[0]
    return id + 1


def _get_fixture_file(path, pattern):
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                return os.path.join(root, name)


def replace_sql_in_revision(path, package, name, session):
    content = None
    sql = []
    modul_fixture = get_modul_fixture(name, package, session)
    modul_sql = ("INSERT INTO modules (id, name, description, label, ",
                 "label_plural, clazzpath, display, str_repr, uuid) ",
                 "VALUES ({id}, '{name}', '', '{label}', '{label_plural}', ",
                 "'{clazzpath}', '{display}', '{str_repr}', '{uuid}');")
    sql.append("".join(modul_sql).format(**modul_fixture))
    modul_id = modul_fixture["id"]
    actions_sql = []
    for fixture in get_action_fixtures(session, modul_id, ignore=[]):
        action_sql = ("INSERT INTO actions (id, mid, uuid, name, url, ",
                      "icon, bundle, description, display, permission) ",
                      "VALUES ({id}, {mid}, '{uuid}', '{name}', ",
                      "'{url}', '{icon}', '{bundle}', '', '{display}', '{permission}');")
        actions_sql.append("".join(action_sql).format(**fixture))
    sql.append("\n".join(actions_sql))
    with open(path, "r") as rf:
        print 'Adding data to revision "%s"... ' % path,
        content = rf.read()
        content = content.replace('INSERTS = """"""',
                                  'INSERTS = """\n%s\n"""' % "\n".join(sql))

    with open(path, "r+") as rf:
        rf.seek(0)
        rf.write(content)

    print 'Ok'


def add_fixtures(package, name, session):
    """Will add the fixtures for the new modul to the fixture files.

    :package: @todo
    :name: @todo
    :session: @todo
    :returns: @todo

    """
    path = os.path.join(get_app_location(package), package, 'fixtures')
    modul_fixture = get_modul_fixture(name, package, session)
    modul_file = _get_fixture_file(path, "*_modules.json")

    with open(modul_file, "r+") as mf:
        print 'Adding data to fixture "%s"... ' % modul_file,
        modul_json = json.load(mf)
        modul_json.append(modul_fixture)
        mf.seek(0)
        mf.write(json.dumps(modul_json, indent=4))
        print 'Ok'

    modul_id = modul_fixture["id"]
    action_fixtures = get_action_fixtures(session, modul_id)
    action_file = _get_fixture_file(path, "*_actions.json")

    with open(action_file, "r+") as af:
        print 'Adding data to fixture "%s"... ' % action_file,
        action_json = json.load(af)
        action_json.extend(action_fixtures)
        af.seek(0)
        af.write(json.dumps(action_json, indent=4))
        print 'Ok'


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
    add_model_file(package, name, modul_id, clazz, args.mixin)
    add_form_file(package, name)
    add_table_file(package, name)
    msg = "Added %s modul" % name
    path = create_new_revision(args, msg)
    replace_sql_in_revision(path, package, name, session)
    print ""
    print "Ready. Next steps:"
    print ""
    print "touch %s" % path
    print "%s-admin db upgrade" % args.app
