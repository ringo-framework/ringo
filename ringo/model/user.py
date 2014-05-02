import logging
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
    _sql_eager_loads = ['roles', 'groups']
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

    def has_role(self, role, include_group_roles=True):
        """Return True if the user has the given role. Else False"
        :user: User instance
        :include_group_roles: Boolean flag to configure if the roles of
        the groups the user is member of should be checked too.
        Defaults to True.
        :returns: True or False
        """
        roles = [r.name for r in self.get_roles(include_group_roles)]
        return role in roles

    def get_roles(self, include_group_roles=True):
        """Returns a list of roles the user has. The list contains
        `Role` object and are collected by loading roles directly
        attached to the user plus optionally roles attached to the
        groups the user is member of

        :include_group_roles: Booloan flag to configure if the roles of
        the groups the user is member of should be included in the list.
        Defaults to True.
        :returns: List of `Role` instances
        """
        tmp_roles = {}

        # Add roles directly attached to the user.
        for urole in self.roles:
            if urole.name not in tmp_roles:
                tmp_roles[urole.name] = urole

        # Add roles attached to the users groups.
        if include_group_roles:
            for group in self.groups:
                for grole in group.get_roles():
                    if grole.name not in tmp_roles:
                        tmp_roles[grole.name] = grole

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

    def get_roles(self):
        """Returns a list of roles the group has. The list contains
        `Role` object and are collected by loading roles directly
        attached to the group.

        :returns: List of `Role` instances
        """
        tmp_roles = {}
        # Add roles directly attached to the group.
        for role in self.roles:
            if role.name not in tmp_roles:
                tmp_roles[role.name] = role
        return list(tmp_roles.values())


class Role(BaseItem, Base):
    __tablename__ = 'roles'
    _modul_id = 5
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Text, unique=True, nullable=False)
    admin = sa.Column(sa.Boolean, default=False)
    """Flag to set the role as administrational role which means that
    the user will gain the assigned permissions irrespective from
    checking the ownership"""

    permissions = sa.orm.relation(ActionItem,
                                  secondary=nm_action_roles,
                                  backref='roles')


class Profile(BaseItem, Owned, Base):
    __tablename__ = 'profiles'
    _modul_id = 6
    id = sa.Column(sa.Integer, primary_key=True)
    first_name = sa.Column(sa.Text, nullable=True)
    last_name = sa.Column(sa.Text, nullable=True)
    gender = sa.Column(sa.Integer)
    birthday = sa.Column(sa.Date)
    address = sa.Column(sa.Text)
    phone = sa.Column(sa.Text)
    email = sa.Column(sa.Text, nullable=True)
    web = sa.Column(sa.Text)

    # The foreign key to the user is injected from the Owned mixin.
    user = sa.orm.relation("User", cascade="all, delete",
                           backref=sa.orm.backref("profile", cascade="all, delete-orphan"),
                           single_parent=True,
                           uselist=False)
