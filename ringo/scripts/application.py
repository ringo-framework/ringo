import os
import transaction
from ringo.scripts.db import get_session
from ringo.lib.helpers import get_app_location, dynamic_import, get_modul_by_name
from ringo.lib.extension import _add_modul
from ringo.model import extensions


def handle_app_init_command(args):
    # Create a folder for the application
    os.makedirs(args.name)
    print("Created new application folder %s" % args.name)

    # Get template for the configuration file.
    template_path = []
    template_path.append(get_app_location(args.app))
    template_path.append(args.app)
    template_path.append("scaffolds")
    template_path.append("basic")
    template_path.append("development.ini_tmpl")

    with open(os.path.join(*template_path)) as f:
        template = f.read()

    config_file = "production.ini"
    config_path = []
    config_path.append(args.name)
    config_path.append(config_file)
    with open(os.path.join(*config_path), "w") as c:
        template = template.replace("{{package}}", args.app)
        #template = template.replace("app.title = ringo", "app.title = %s"
        #                            % args.name)
        c.write(template)
    print("Created new configuration file %s in %s" % (config_file, args.name))

    print("\n")
    print("Next steps:")
    print("0. cd %s" % args.name)
    print("1. Adjust settings in your config")
    print("2. %s-admin db init --config %s" % (args.app, config_file))
    print("3. %s-admin fixtures load --config %s" % (args.app, config_file))
    print("4. Start application: pserve production.ini")


def handle_ext_init_command(args):
    path = []
    path.append(get_app_location(args.app))
    path.append(args.config)
    session = get_session(os.path.join(*path))
    for ext in extensions:
        if ext == args.name:
            if get_modul_by_name(ext.replace("ringo_", ""), session):
                print "Extension %s already added!" % args.name
            else:
                extension = dynamic_import("%s." % args.name)
                _add_modul(extension.modul_config, None, session)
                print "Extension %s added!" % args.name
            break
    else:
        print "Extension %s not found!" % args.name


def handle_ext_delete_command(args):
    path = []
    path.append(get_app_location(args.app))
    path.append(args.config)
    session = get_session(os.path.join(*path))
    modul = get_modul_by_name(args.name.replace("ringo_", ""), session)
    if modul:
        if args.name in extensions:
            session.delete(modul)
            transaction.commit()
            print "Extension %s deleted!" % args.name
        else:
            print "Extension %s already deleted!" % args.name
    else:
        print "Extension %s not found!" % args.name
