import hashlib
import random
import string
import sqlalchemy as sa
from datetime import datetime
from ringo.model import Base
from ringo.model.base import BaseItem, BaseFactory
from ringo.model.modul import ActionItem, ModulItem
from ringo.model.mixins import Owned


password_reset_requests = sa.Table(
    'password_reset_requests', Base.metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('uid', sa.Integer, sa.ForeignKey('users.id')),
    sa.Column('created', sa.DateTime),
    sa.Column('token', sa.Text)
)

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

nm_action_roles = sa.Table(
    'nm_action_roles', Base.metadata,
    sa.Column('aid', sa.Integer, sa.ForeignKey('actions.id')),
    sa.Column('rid', sa.Integer, sa.ForeignKey('roles.id'))
)


class PasswordResetRequest(Base):
    __tablename__ = 'password_reset_requests'
    user = sa.orm.relationship("User", backref='reset_tokens')

    def __init__(self, token):
        self.token = token
        self.created = datetime.now()

    def __str__(self):
        return self.token


class UserFactory(BaseFactory):

    def create(self, user=None):
        new_user = BaseFactory.create(self, user)
        # Now create a a new Profile
        profile_factory = BaseFactory(Profile)
        profile = profile_factory.create(user)
        new_user.profile.append(profile)
        return new_user


class User(BaseItem, Base):
    __tablename__ = 'users'
    _modul_id = 3
    id = sa.Column(sa.Integer, primary_key=True)
    login = sa.Column(sa.Text, unique=True, nullable=False)
    password = sa.Column(sa.Text, nullable=False)
    activated = sa.Column(sa.Boolean, default=True)
    activation_token = sa.Column(sa.Text)
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

    @classmethod
    def get_item_factory(cls):
        return UserFactory(cls)

    def __unicode__(self):
        return self.login


ADMIN_GROUP_ID = 1
"""Role ID your the system administration group"""
USER_GROUP_ID = 2
"""Role ID your the system user group"""


class Usergroup(BaseItem, Base):
    __tablename__ = 'usergroups'
    _modul_id = 4
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
    _modul_id = 5
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Text, unique=True, nullable=False)
    admin = sa.Column(sa.Boolean, default=False)
    """Flag to set the role as administrational role which means that
    the user will gain the assigned permissions irrespective from
    checking the ownership"""

    # Configuration
    _table_fields = [('name', 'Name')]

    permissions = sa.orm.relation(ActionItem, secondary=nm_action_roles)

    def __unicode__(self):
        return self.name


class Profile(BaseItem, Owned, Base):
    __tablename__ = 'profiles'
    _modul_id = 6
    id = sa.Column(sa.Integer, primary_key=True)
    first_name = sa.Column(sa.Text, nullable=True)
    last_name = sa.Column(sa.Text, nullable=True)
    birthday = sa.Column(sa.Date)
    address = sa.Column(sa.Text)
    phone = sa.Column(sa.Text)
    email = sa.Column(sa.Text, nullable=True)
    web = sa.Column(sa.Text)

    # The foreign key to the user is injected from the Owned mixin.
    user = sa.orm.relation("User", cascade="all, delete-orphan",
                           backref="profile", single_parent=True,
                           uselist=False)

    # Configuration
    _table_fields = [('first_name', 'last_name', 'email')]

    def __unicode__(self):
        return "%s %s" % (self.first_name, self.last_name)


def init_model(dbsession):
    """Will setup the initial model for the usermanagement. This
    includes creating users, usergroups  roles and permissions.

    :dbsession: Database session to which the items will be added.
    :returns: None

    """
    # Admin Role
    ############
    admin_role = Role(name='admin', admin=True)
    dbsession.add(admin_role)

    # User Role
    ###########
    role = Role(name='user')
    dbsession.add(role)
    # Load profiles modul
    modul = ModulItem.get_item_factory().load(Profile._modul_id)
    # Add permissions to edit and read the users profiles
    role.permissions.append(modul.actions[1])
    role.permissions.append(modul.actions[2])

    # Admin group
    #############
    admin_usergroup = Usergroup(name='admins')
    admin_usergroup.roles.append(admin_role)
    dbsession.add(admin_usergroup)

    # User group
    ############
    usergroup = Usergroup(name='users')
    usergroup.roles.append(role)
    dbsession.add(usergroup)

    # Admin user
    ############
    pw = hashlib.md5()
    pw.update('secret')
    user = User(login='admin', password=pw.hexdigest())
    user.activation_token = "0e3cc848-22f6-4ff7-a562-12baf3037439"
    user.default_group = admin_usergroup
    user.groups.append(admin_usergroup)
    dbsession.add(user)

    # Admin profile
    ###############
    profile = Profile()
    profile.first_name = "Firstname"
    profile.last_name = "Lastname"
    profile.email = "mail@example.com"
    profile.user = user
    dbsession.add(profile)

    ## Performance tests (not needed in production use)
    ###################################################
    #for i in range(100):
    #    login = ''.join(random.choice(string.ascii_uppercase
    #                                  + string.digits) for x in range(8))
    #    pw.update(login)
    #    user = User(login=login, password=pw.hexdigest())
    #    user.default_group = admin_usergroup
    #    user.groups.append(admin_usergroup)
    #    dbsession.add(user)
    #    profile = Profile()
    #    profile.first_name = "Firstname-%s" % i
    #    profile.last_name = "Lastname-%s" % i
    #    profile.email = "mail-%s@example.com" % i
    #    profile.user = user
    #    dbsession.add(profile)
