import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from ringo.lib.sql import (
    DBSession,
)

from ringo.model import (
    Base,
)

from ringo.model.user import (
    init_model as init_user_model,
)
from ringo.model.modul import (
    init_model as init_modul_model,
)
from ringo.model.appointment import (
    init_model as init_appointment_model
)
from ringo.model.file import (
    init_model as init_file_model
)
from ringo.model.news import (
    init_model as init_news_model
)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    inititializedb(engine)


def inititializedb(engine):
    Base.metadata.create_all(engine)
    DBSession.configure(bind=engine)
    with transaction.manager:
        init_modul_model(DBSession)
        init_user_model(DBSession)
        init_appointment_model(DBSession)
        init_file_model(DBSession)
        init_news_model(DBSession)

