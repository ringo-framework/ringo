from invoke import run
from ringo.scripts.helpers import get_db, get_package_name, get_fixtures


def handle_fixture_load_command(args):
    appname = get_package_name(args.config)
    db = get_db(args.config)
    print "Loading data in %s" % db
    for fixture, modul in get_fixtures(args.app, args.path):
        print "Loading fixture %s" % fixture
        run("%s-admin db loaddata --loadbyid --config %s %s %s" % (appname, args.config, modul, fixture))


def handle_fixture_save_command(args):
    appname = get_package_name(args.config)
    db = get_db(args.config)
    print "Saving data in %s" % db
    for fixture, modul in get_fixtures(args.app, args.path):
        print "Saving fixture %s" % fixture
        print("%s-admin db savedata --config %s %s > %s" %
            (appname, args.config, modul, fixture))
        run("%s-admin db savedata --config %s %s > %s" %
            (appname, args.config, modul, fixture))
        run("python -m json.tool %s > %s.tmp" % (fixture, fixture))
        run("mv %s.tmp %s" % (fixture, fixture))
