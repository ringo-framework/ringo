import os
import transaction
from mako.lookup import TemplateLookup
from ringo.config import modul_template_dir
from ringo.lib.helpers import get_app_location
from ringo.scripts.db import get_session
from ringo.model.modul import ModulItem, ActionItem
template_lookup = TemplateLookup(directories=[modul_template_dir])


def _create_default_actions(session, ignore=[]):
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
        session.add(a0)
        actions.append(a0)
    if not "create" in ignore:
        session.add(a1)
        actions.append(a1)
    if not "read" in ignore:
        session.add(a2)
        actions.append(a2)
    if not "update" in ignore:
        session.add(a3)
        actions.append(a3)
    if not "delete" in ignore:
        session.add(a4)
        actions.append(a4)
    if not "import" in ignore:
        session.add(a5)
        actions.append(a5)
    if not "export" in ignore:
        session.add(a6)
        actions.append(a6)
    return actions

def remove_db_entry(name, session):
    print 'Remove entry in modules table for "%s"... ' % name,
    modul_name = name + "s"
    try:
        with transaction.manager:
            modul = session.query(ModulItem).filter(ModulItem.name == modul_name).delete()
            session.flush()
        # Get last inserted id.
        print 'Ok.'
    except Exception, e:
        print e
        print 'Failed.'

def add_db_entry(package, name, session):
    print 'Adding new entry in modules table for "%s"... ' % name,
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
            modul.actions.extend(_create_default_actions(session))
            session.add(modul)
            session.flush()
        # Get last inserted id.
        last_modul = session.query(ModulItem).filter(ModulItem.name == modul_name).one()
        print 'Ok.'
        return last_modul.id
    except Exception, e:
        print e
        print 'Failed.'


def del_model_file(package, modul):
    target_file = os.path.join(get_app_location(package), package, 'model', '%s.py' % modul)
    print 'Deleting model file "%s"... ' % target_file,
    try:
        os.remove(target_file)
        print 'Ok.'
    except Exception:
        print 'Failed.'


def add_model_file(package, modul, id, clazz):
    target_file = os.path.join(get_app_location(package), package, 'model', '%s.py' % modul)
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


def del_form_file(package, modul):
    filename = modul + "s"
    target_file= os.path.join(get_app_location(package), package, 'views', 'forms', '%s.xml' % filename)
    print 'Deleting form configuration file "%s"... ' % target_file,
    try:
        os.remove(target_file)
        print 'Ok.'
    except:
        print 'Failed.'


def add_form_file(package, modul):
    filename = modul + "s"
    target_file= os.path.join(get_app_location(package), package, 'views', 'forms', '%s.xml' % filename)
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
    target_file= os.path.join(get_app_location(package), package, 'views', 'tables', '%s.json' % filename)
    print 'Deleting table configuration file "%s"... ' % target_file,
    try:
        os.remove(target_file)
        print 'Ok.'
    except:
        print 'Failed.'


def add_table_file(package, modul):
    filename = modul + "s"
    target_file= os.path.join(get_app_location(package), package, 'views', 'tables', '%s.json' % filename)
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
    modul_id = add_db_entry(package, name, session)
    add_model_file(package, name, modul_id, clazz)
    add_form_file(package, name)
    add_table_file(package, name)
