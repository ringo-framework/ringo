import hashlib
from ringo.model import Base, sqlalchemy as sa


class User(Base):
    __tablename__ = 'users'
    id = sa.Column(sa.Integer, primary_key=True)
    login = sa.Column(sa.Text, unique=True, nullable=False)
    password = sa.Column(sa.Text, nullable=False)


class Usergroup(Base):
    __tablename__ = 'usergroups'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Text, unique=True, nullable=False)


class Role(Base):
    __tablename__ = 'roles'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Text, unique=True, nullable=False)


class Permission(Base):
    __tablename__ = 'permissions'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Text, unique=True, nullable=False)


def init_model(dbsession):
    """Will setup the initial model for the usermanagement. This
    includes creating users, usergroups  roles and permissions.

    :dbsession: Database session to which the items will be added.
    :returns: None

    """
    pw = hashlib.md5()
    pw.update('secret')
    user = User(login='admin', password=pw.hexdigest())
    dbsession.add(user)
    usergroup = Usergroup(name='admins')
    dbsession.add(usergroup)
    usergroup = Usergroup(name='users')
    dbsession.add(usergroup)
    role = Role(name='admin')
    dbsession.add(role)
    role = Role(name='user')
    dbsession.add(role)
    read_perm = Permission(name='create')
    create_perm = Permission(name='read')
    update_perm = Permission(name='update')
    delete_perm = Permission(name='delete')
    dbsession.add(read_perm)
    dbsession.add(create_perm)
    dbsession.add(update_perm)
    dbsession.add(delete_perm)
