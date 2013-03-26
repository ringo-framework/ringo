import hashlib
import random
import string
from formbar.config import Config, load
from ringo.model import Base, sqlalchemy as sa
from ringo.lib.helpers import get_path_to_form_config

# NM-Table definitions
nm_user_roles = sa.Table(
    'nm_user_roles', Base.metadata,
    sa.Column('uid', sa.Integer, sa.ForeignKey('users.id')),
    sa.Column('rid', sa.Integer, sa.ForeignKey('roles.id'))
)

nm_usergroup_roles = sa.Table(
    'nm_usergroup_roles', Base.metadata,
    sa.Column('gid', sa.Integer, sa.ForeignKey('usergroups.id')),
    sa.Column('rid', sa.Integer, sa.ForeignKey('roles.id'))
)

nm_user_usergroups = sa.Table(
    'nm_user_usergroups', Base.metadata,
    sa.Column('uid', sa.Integer, sa.ForeignKey('users.id')),
    sa.Column('gid', sa.Integer, sa.ForeignKey('usergroups.id'))
)

nm_role_permissions = sa.Table(
    'nm_role_permissions', Base.metadata,
    sa.Column('rid', sa.Integer, sa.ForeignKey('roles.id')),
    sa.Column('pid', sa.Integer, sa.ForeignKey('permissions.id'))
)


class BaseItem(object):

    def __str__(self):
        return self.__unicode__()

    @classmethod
    def get_table_config(cls):
        return cls._table_fields

    @classmethod
    def get_form_config(cls, formname):
        cfile = "%s.xml" % cls.__tablename__
        config = Config(load(get_path_to_form_config(cfile)))
        return config.get_form(formname)

    @classmethod
    def get_action_routename(cls, action):
        return "%s-%s" % (cls.__tablename__, action)


class User(BaseItem, Base):
    __tablename__ = 'users'
    id = sa.Column(sa.Integer, primary_key=True)
    login = sa.Column(sa.Text, unique=True, nullable=False)
    password = sa.Column(sa.Text, nullable=False)
    gid = sa.Column(sa.Integer, sa.ForeignKey('usergroups.id'))

    # Relations
    roles = sa.orm.relationship("Role",
                                secondary=nm_user_roles)
    groups = sa.orm.relationship("Usergroup",
                                 secondary=nm_user_usergroups,
                                 backref='members')
    default_group = sa.orm.relationship("Usergroup", uselist=False)

    # Configuration
    _table_fields = [('login', 'Login'),
                     ('roles', 'Roles'),
                     ('groups', 'Groups')]

    def __unicode__(self):
        return self.login

    def get_roles(self):
        """Returns a list of roles the user has. The list contains
        `Role` object and are collected by loading roles directly
        attached to the user plus roles attached to the groups the user
        is member of

        :returns: List of `Role` instances

        """
        tmp_roles = {}

        # Add roles directly attached to the user.
        for role in self.roles:
            if role.name not in tmp_roles:
                tmp_roles[role.name] = role

        # Add roles directly attached to the user.
        for group in self.groups:
            for role in group.roles:
                if role.name not in tmp_roles:
                    tmp_roles[role.name] = role

        return list(tmp_roles.values())


class Usergroup(BaseItem, Base):
    __tablename__ = 'usergroups'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Text, unique=True, nullable=False)

    # Relations
    roles = sa.orm.relationship("Role", secondary=nm_usergroup_roles)

    # Configuration
    _table_fields = [('name', 'Login'),
                     ('roles', 'Roles')]

    def __unicode__(self):
        return self.name


class Role(BaseItem, Base):
    __tablename__ = 'roles'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Text, unique=True, nullable=False)

    # Relations
    permissions = sa.orm.relationship("Permission",
                                      secondary=nm_role_permissions)

    def __unicode__(self):
        return self.name


class Permission(BaseItem, Base):
    __tablename__ = 'permissions'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Text, unique=True, nullable=False)

    def __unicode__(self):
        return self.name


def init_model(dbsession):
    """Will setup the initial model for the usermanagement. This
    includes creating users, usergroups  roles and permissions.

    :dbsession: Database session to which the items will be added.
    :returns: None

    """
    read_perm = Permission(name='read')
    create_perm = Permission(name='create')
    update_perm = Permission(name='update')
    delete_perm = Permission(name='delete')
    dbsession.add(read_perm)
    dbsession.add(create_perm)
    dbsession.add(update_perm)
    dbsession.add(delete_perm)
    admin_role = Role(name='admin')
    admin_role.permissions.append(create_perm)
    admin_role.permissions.append(read_perm)
    admin_role.permissions.append(update_perm)
    admin_role.permissions.append(delete_perm)
    dbsession.add(admin_role)
    role = Role(name='user')
    dbsession.add(role)
    admin_usergroup = Usergroup(name='admins')
    admin_usergroup.roles.append(admin_role)
    dbsession.add(admin_usergroup)
    usergroup = Usergroup(name='users')
    dbsession.add(usergroup)
    pw = hashlib.md5()
    pw.update('secret')
    user = User(login='admin', password=pw.hexdigest())
    user.default_group = admin_usergroup
    user.groups.append(admin_usergroup)
    dbsession.add(user)
    #Performance tests
    for i in range(100):
        login = ''.join(random.choice(string.ascii_uppercase
                                      + string.digits) for x in range(8))
        pw.update(login)
        user = User(login=login, password=pw.hexdigest())
        user.default_group = admin_usergroup
        user.groups.append(admin_usergroup)
        dbsession.add(user)
