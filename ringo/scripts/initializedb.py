import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from ..models import (
    DBSession,
    User,
    Usergroup,
    Role,
    Permission,
    MyModel,
    Base,
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
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        model = MyModel(name='one', value=1)
        DBSession.add(model)
        user = User(login='admin', password='secret')
        DBSession.add(user)
        usergroup = Usergroup(name='admins')
        DBSession.add(usergroup)
        usergroup = Usergroup(name='users')
        DBSession.add(usergroup)
        role = Role(name='admin')
        DBSession.add(role)
        role = Role(name='user')
        DBSession.add(role)
        read_perm = Permission(name='create')
        create_perm = Permission(name='read')
        update_perm = Permission(name='update')
        delete_perm = Permission(name='delete')
        DBSession.add(read_perm)
        DBSession.add(create_perm)
        DBSession.add(update_perm)
        DBSession.add(delete_perm)
