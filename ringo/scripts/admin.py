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

import logging
import os
import argparse
from alembic.config import Config
from alembic import command
from ringo.lib.helpers import get_app_location

log = logging.getLogger(__name__)


def handle_db_init_command(args):
    cfg = Config("alembic.ini")
    ringo_path = get_app_location("ringo")
    cfg.set_main_option("script_location",
                        os.path.join(ringo_path, "alembic"))
    command.upgrade(cfg, "head")


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


def setup_global_argument_parser():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--config',
                        default="development.ini",
                        metavar="INI",
                        help="Configuration file for the application")
    return parser


def setup_parser():
    parser = argparse.ArgumentParser(description="Administrate various "
                                     "aspects in a ringo based application.")
    global_arguments = setup_global_argument_parser()
    subparsers = parser.add_subparsers(help='sub-command help')
    setup_db_parser(subparsers, global_arguments)
    return parser


def main():
    parser = setup_parser()
    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()

# vim: ai ts=4 sts=4 et sw=4
