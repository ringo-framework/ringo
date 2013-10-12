import logging
import hashlib
import json
import sqlalchemy as sa
from datetime import datetime
from ringo.model import Base
from ringo.model.base import BaseItem, BaseFactory
from ringo.model.modul import ActionItem, ModulItem
from ringo.model.mixins import Owned


log = logging.getLogger(__name__)


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

class UserSetting(Base):
    __tablename__ = 'user_settings'

    id = sa.Column(sa.Integer, primary_key=True)
    settings = sa.Column(sa.Text, nullable=False, default="{}")

    def get(self, key, default):
        log.debug("Getting usersetting")
        settings = json.loads(self.settings)
        return settings.get(key, default)

    def set(self, key, value):
        settings = json.loads(self.settings)
        section = settings.get(key)
        section = value
        settings[key] = section
        dump = json.dumps(settings)
        log.debug("Setting usersetting for %s: %s" % (key, dump))
        self.settings = dump

class UserFactory(BaseFactory):

    def create(self, user=None):
        new_user = BaseFactory.create(self, user)
        # Now create a a new Profile
        profile_factory = BaseFactory(Profile)
        settings_factory = BaseFactory(UserSetting)
        settings = settings_factory.create(user)
        profile = profile_factory.create(user)
        new_user.profile.append(profile)
        new_user.settings = settings
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
    sid = sa.Column(sa.Integer, sa.ForeignKey('user_settings.id'))

    # Relations
    roles = sa.orm.relationship("Role",
                                secondary=nm_user_roles)
    groups = sa.orm.relationship("Usergroup",
                                 secondary=nm_user_usergroups,
                                 backref='members')
    default_group = sa.orm.relationship("Usergroup", uselist=False)
    settings = sa.orm.relationship("UserSetting", uselist=False,
                                   cascade="all,delete")

    @classmethod
    def get_item_factory(cls):
        return UserFactory(cls)

    def __unicode__(self):
        return self.login

    def has_role(self, role):
        """Return True if the user has the given role. Else False"
        :user: User instance
        :returns: True or False
        """
        roles = [r.name for r in self.get_roles()]
        return role in roles

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

    permissions = sa.orm.relation(ActionItem, secondary=nm_action_roles, backref='roles')

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
    user.settings = UserSetting()
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
