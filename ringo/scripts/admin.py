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

from ringo.scripts.db import (
    handle_db_init_command,
    handle_db_upgrade_command
)

from ringo.scripts.modul import (
    handle_modul_add_command,
    handle_modul_delete_command,
)

def modul_name(var):
    return str(var).lower()

def setup_modul_parser(subparsers, parent):
    p = subparsers.add_parser('modul',
                              help='Modul administration',
                              parents=[parent])
    sp = p.add_subparsers(help='Modul command help')

    # Add command
    add_parser = sp.add_parser('add',
                                help='Adds a new modul',
                                parents=[parent])
    add_parser.add_argument('name',
                            type=modul_name,
                            help='Name of the new modul (singular form)')
    add_parser.set_defaults(func=handle_modul_add_command)

    # Add command
    delete_parser = sp.add_parser('delete',
                                  help='Deletes a modul',
                                  parents=[parent])
    delete_parser.add_argument('name',
                               type=modul_name,
                               help='Name of the modul to delete')
    delete_parser.set_defaults(func=handle_modul_delete_command)


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


def setup_global_argument_parser():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--app',
                        default=_get_app_name(),
                        metavar="APP",
                        help="Name of the application")
    parser.add_argument('--config',
                        default="development.ini",
                        metavar="INI",
                        help="Configuration file for the application")
    return parser


def setup_parser():
    parser = argparse.ArgumentParser(description="Administrate various "
                                     "aspects in a ringo based application.")
    global_arguments = setup_global_argument_parser()
    subparsers = parser.add_subparsers(help='Command help')
    setup_db_parser(subparsers, global_arguments)
    setup_modul_parser(subparsers, global_arguments)
    return parser


def _get_app_name():
    """@todo: Docstring for _get_app_name.
    :returns: @todo

    """
    return sys.argv[0].split("/")[-1].split("-")[0]


def main():
    parser = setup_parser()
    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()

# vim: ai ts=4 sts=4 et sw=4
