import os
import transaction
from ringo.scripts.db import get_session
from ringo.lib.helpers import get_app_location
from ringo.model.user import User
from ringo.lib.security import encrypt_password, password_generator


def handle_user_passwd_command(args):
    if args.password:
        password = args.password
    else:
        password = password_generator()
    encrypted_password = encrypt_password(password)
    path = []
    path.append(get_app_location(args.app))
    path.append(args.config)
    session = get_session(os.path.join(*path))
    user = session.query(User).filter(User.login == args.user).all()[0]
    user.password = encrypted_password
    transaction.commit()
    print "OK! Password for '%s' changed to '%s'" % (args.user, password)
