import os
from invoke import run
import pkg_resources

def get_package_location(name):
    return pkg_resources.get_distribution(name).location

def get_package_name(config_file):
    result = run("sed -n 's|^use = egg:\\([[:graph:]]*\\).*|\\1|p' %s | head -1" % config_file, hide="out")
    return result.stdout.strip()


def get_db(config_file):
    result = run("sed -n 's|^sqlalchemy.url.*//.*@.*/\\([[:graph:]]*\\).*|\\1|p' %s" % config_file, hide="out")
    return result.stdout.strip()


def get_fixtures(appname):
    apppath = os.path.join(get_package_location(appname), appname)
    result = run("ls %s/fixtures/*.json" % apppath, hide="out").stdout.strip()
    fixtures = []
    for fixture in sorted(result.split("\n")):
        fixtures.append((fixture, fixture.split("_")[1].split(".")[0]))
    return fixtures
