#!/usr/bin/python
# Copyright (C) 2014 Torsten Irlaender <torsten@irlaender.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston,
# MA 02111-1307, USA.

"""
This is a short description of what this script does.
"""

import os
import sys
import argparse
from pyramid import testing
from pyramid.registry import Registry
from paste.deploy.loadwsgi import appconfig

from ringo.scripts.db import (
    handle_db_init_command,
    handle_db_revision_command,
    handle_db_upgrade_command,
    handle_db_downgrade_command,
    handle_db_savedata_command,
    handle_db_loaddata_command,
    handle_db_uuid_command,
    handle_db_restrict_command,
    handle_db_unrestrict_command,
    handle_db_fixsequence_command
)

from ringo.scripts.fixture import (
    handle_fixture_load_command,
    handle_fixture_save_command
)

from ringo.scripts.modul import (
    handle_modul_add_command,
    handle_modul_delete_command,
    handle_modul_fields_command,
)

from ringo.scripts.user import (
    handle_user_passwd_command
)

from ringo.scripts.application import (
    handle_app_init_command,
    handle_ext_init_command,
    handle_ext_delete_command
)

def get_config_path(config="development.ini"):
    return os.path.join(os.getcwd(), config)

def modul_name(var):
    return str(var).lower()

def setup_fixture_parser(subparsers, parent):
    p = subparsers.add_parser('fixtures',
                              help='Fixture loading and saving',
                              parents=[parent])
    sp = p.add_subparsers(help='Fixture command help')

    # Load
    fixture_parser = sp.add_parser('load',
                                help=('Loads all fixture files.'),
                                parents=[parent])
    fixture_parser.set_defaults(func=handle_fixture_load_command)
    fixture_parser.add_argument('--path',
                              metavar='path',
                              help='Path to the fixture files')

    # Save
    fixture_parser = sp.add_parser('save',
                                help=('Saves all fixture files.'),
                                parents=[parent])
    fixture_parser.set_defaults(func=handle_fixture_save_command)
    fixture_parser.add_argument('--path',
                              metavar='path',
                              help='Path to the fixture files')
    return sp


def setup_application_parser(subparsers, parent):
    p = subparsers.add_parser('app',
                              help='Application administration',
                              parents=[parent])
    sp = p.add_subparsers(help='Application command help')

    # Init command
    app_parser = sp.add_parser('init',
                                help=('Initialises an empty application '
                                      'folder and creates a default '
                                      'configuration file in it'),
                                parents=[parent])
    app_parser.add_argument('name',
                              metavar='name',
                              help='Name of the application')
    app_parser.set_defaults(func=handle_app_init_command)

    reg_parser = sp.add_parser('add-extension',
                                help=('Will create modul entries for a given extension'),
                                parents=[parent])
    reg_parser.add_argument('name',
                            metavar='name',
                            help='Name of the extension')
    reg_parser.set_defaults(func=handle_ext_init_command)
    unreg_parser = sp.add_parser('remove-extension',
                                help=('Will delete modul entries for a given extension'),
                                parents=[parent])
    unreg_parser.add_argument('name',
                            metavar='name',
                            help='Name of the extension')
    unreg_parser.set_defaults(func=handle_ext_delete_command)
    return sp


def setup_user_parser(subparsers, parent):
    p = subparsers.add_parser('user',
                              help='User administration',
                              parents=[parent])
    sp = p.add_subparsers(help='User command help')

    # Init command
    passwd_parser = sp.add_parser('passwd',
                                help=('Set the password for a user.'
                                      'Password will be autogenerated unless'
                                      'your provide the password with the '
                                      '--password option.'),
                                parents=[parent])
    passwd_parser.add_argument('user',
                              metavar='user',
                              help='Name of the user')
    passwd_parser.add_argument('--password',
                              metavar='password',
                              help='Password for the user')
    passwd_parser.set_defaults(func=handle_user_passwd_command)
    return sp


def setup_modul_parser(subparsers, parent):
    p = subparsers.add_parser('modul',
                              help='Modul administration',
                              parents=[parent])
    sp = p.add_subparsers(help='Modul command help')
    # Model command
    model_parser = sp.add_parser('fields',
                                 help='Generates the model fields',
                                 parents=[parent])
    model_parser.add_argument('name',
                              type=modul_name,
                              help='Name of the new modul (singular form)')
    model_parser.set_defaults(func=handle_modul_fields_command)

    # Add command
    add_parser = sp.add_parser('add',
                                help='Adds a new modul',
                                parents=[parent])
    add_parser.add_argument('name',
                            type=modul_name,
                            help='Name of the new modul (singular form)')
    add_parser.add_argument('--mixin',
                            nargs="*",
                            choices=['owned', 'meta', 'logged', 'state',
                                     'blob', 'blobform', 'versioned', 'printable',
                                     'nested', 'commented', 'tagged', 'todo'],
                            default=["owned"],
                            help='Mixins for the generated model')
    add_parser.set_defaults(func=handle_modul_add_command)

    # Delete command
    delete_parser = sp.add_parser('delete',
                                  help='Deletes a modul',
                                  parents=[parent])
    delete_parser.add_argument('name',
                               type=modul_name,
                               help='Name of the modul to delete')
    delete_parser.set_defaults(func=handle_modul_delete_command)
    return sp


def setup_db_parser(subparsers, parent):
    p = subparsers.add_parser('db',
                              help='Database administration',
                              parents=[parent])
    sp = p.add_subparsers(help='Database command help')

    # Init command
    init_parser = sp.add_parser('init',
                                help='Initialise a new database',
                                parents=[parent])
    init_parser.set_defaults(func=handle_db_init_command)

    # Upgrade command
    upgrade_parser = sp.add_parser('upgrade',
                                help='Upgrades a database',
                                parents=[parent])
    upgrade_parser.set_defaults(func=handle_db_upgrade_command)

    # Downgrade command
    downgrade_parser = sp.add_parser('downgrade',
                                help='Downgrades a database',
                                parents=[parent])
    downgrade_parser.set_defaults(func=handle_db_downgrade_command)

    # Revision command
    revision_parser = sp.add_parser('revision',
                                help='Creates a new alembic revision command',
                                parents=[parent])
    revision_parser.set_defaults(func=handle_db_revision_command)

    # Savedata command
    savedata_parser = sp.add_parser('savedata',
                                help='Saves the data of a given modul',
                                parents=[parent])
    savedata_parser.set_defaults(func=handle_db_savedata_command)
    savedata_parser.add_argument('modul',
                        metavar="modul",
                        help="Name of the Modul")
    savedata_parser.add_argument('--format',
                        choices=["json", "csv"],
                        default="json",
                        help="Format of the saved data (default json)")
    savedata_parser.add_argument('--filter',
                        help="Define a filter to select which items"
                             " should be included in the export.")
    savedata_parser.add_argument('--export-config',
                        help="Detailed configuration of the content of the export.")

    # restrict command
    savedata_parser = sp.add_parser('restrict',
                                help=('Restrict access to the given modul'
                                     ' on database level'),
                                parents=[parent])
    savedata_parser.set_defaults(func=handle_db_restrict_command)
    savedata_parser.add_argument('modul',
                        metavar="modul",
                        help="Name of the Modul")
    savedata_parser = sp.add_parser('unrestrict',
                                help=('Unrestrict access to the given modul'
                                     ' on database level'),
                                parents=[parent])
    savedata_parser.set_defaults(func=handle_db_unrestrict_command)
    savedata_parser.add_argument('modul',
                        metavar="modul",
                        help="Name of the Modul")

    # Loaddata command
    loaddata_parser = sp.add_parser('loaddata',
                                help='Loads the data of a given modul',
                                parents=[parent])
    loaddata_parser.set_defaults(func=handle_db_loaddata_command)
    loaddata_parser.add_argument('modul',
                        metavar="modul",
                        help="Name of the Modul")
    loaddata_parser.add_argument('fixture',
                        metavar="fixture",
                        help="Path to the importfile")
    loaddata_parser.add_argument('--loadbyid',
                        action="store_true",
                        help="Load data by id and not by uuid")
    loaddata_parser.add_argument('--format',
                        choices=["json", "csv"],
                        default="json",
                        help="Format of the loaded data (default json)")

    # UUID command
    uuid_parser = sp.add_parser('resetuuid',
                                help='Generates UUID for data of a given modul',
                                parents=[parent])
    uuid_parser.set_defaults(func=handle_db_uuid_command)
    uuid_parser.add_argument('modul',
                        metavar="modul",
                        help="Name of the Modul")
    uuid_parser.add_argument('--missing-only',
                        action="store_true",
                        help="Reset the UUID only where it is not already set.")

    # Fix sequence command
    upgrade_parser = sp.add_parser('fixsequence',
                                help='Fixes sequences in postgres databases',
                                parents=[parent])
    upgrade_parser.set_defaults(func=handle_db_fixsequence_command)
    return sp


def setup_global_argument_parser():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--app',
                        default=_get_app_name(),
                        metavar="APP",
                        help="Name of the application")
    parser.add_argument('--base',
                        default="ringo",
                        metavar="BASEAPP",
                        help="Name of the base application")
    parser.add_argument('--config',
                        default=get_config_path(),
                        metavar="INI",
                        help="Configuration file for the application")
    return parser


def setup_parser():
    parser = {}
    parser["root"] = argparse.ArgumentParser(description="Administrate "
                                             "various aspects in a ringo "
                                             "based application.")
    global_arguments = setup_global_argument_parser()
    subparsers = parser["root"].add_subparsers(help='Command help')

    parser["db"] = setup_db_parser(subparsers, global_arguments)
    parser["modul"] = setup_modul_parser(subparsers, global_arguments)
    parser["user"] = setup_user_parser(subparsers, global_arguments)
    parser["app"] = setup_application_parser(subparsers, global_arguments)
    parser["fixture"] = setup_fixture_parser(subparsers, global_arguments)
    return (parser, subparsers, global_arguments)


def _get_app_name():
    """@todo: Docstring for _get_app_name.
    :returns: @todo

    """
    return sys.argv[0].split("/")[-1].split("-")[0]


def main():
    parser, subparsers, global_arguments = setup_parser()
    args = parser["root"].parse_args()
    # FIXME: Initialialising the testing modul is currently the only
    # known way to make the settings
    # available in the current_registry call (which is called
    # inside
    # ringo when loading the form).
    config = appconfig('config:%s' % args.config, "main", relative_to='.')
    name = config.context.distribution.project_name
    registry = Registry(name)
    registry.settings = config
    testing.setUp(registry)

    args.func(args)

if __name__ == '__main__':
    main()

# vim: ai ts=4 sts=4 et sw=4
