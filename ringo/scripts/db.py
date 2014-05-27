import os
from sqlalchemy import engine_from_config
from alembic.config import Config
from alembic import command
from pyramid.paster import (
    get_appsettings,
    setup_logging,
)
from ringo.lib.sql import DBSession
from ringo.lib.helpers import get_app_location

def get_engine(config_file):
    setup_logging(config_file)
    settings = get_appsettings(config_file)
    engine = engine_from_config(settings, 'sqlalchemy.')
    return engine

def get_session(config_file):
    engine = get_engine(config_file)
    DBSession.configure(bind=engine)
    return DBSession

def get_alembic_config(args, app=None):
    """Return a alembic configuration

    :app: Name of the application
    :returns: Alembic configuration

    """

    config_path = []
    config_path.append(get_app_location(args.app))
    config_path.append("alembic.ini")
    cfg = Config(os.path.join(*config_path))

    script_path = []
    if app:
        script_path.append(get_app_location(app))
    script_path.append("alembic")
    cfg.set_main_option("script_location", os.path.join(*script_path))
    return cfg


def handle_db_init_command(args):
    cfg = get_alembic_config(args, "ringo")
    command.upgrade(cfg, "head")
    cfg = get_alembic_config(args)
    command.stamp(cfg, "head")
    handle_db_upgrade_command(args)


def handle_db_upgrade_command(args):
    cfg = get_alembic_config(args)
    command.upgrade(cfg, "head")
