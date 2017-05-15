import logging
import json
import sqlalchemy as sa
from datetime import datetime
from ringo.lib.alchemy import get_prop_from_instance
from ringo.model import Base
from ringo.model.base import BaseItem, BaseFactory
from ringo.model.mixins import Owned


log = logging.getLogger(__name__)


password_reset_requests = sa.Table(
    'password_reset_requests', Base.metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('uid', sa.Integer, sa.ForeignKey('users.id')),
    sa.Column('created', sa.DateTime),
    sa.Column('token', sa.String)
)

# NM-Table definitions
nm_user_roles = sa.Table(
    'nm_user_roles', Base.metadata,
    sa.Column('uid', sa.Integer, sa.ForeignKey('users.id')),
    sa.Column('rid', sa.Integer, sa.ForeignKey('roles.id')),
    sa.UniqueConstraint('uid', 'rid')
)

nm_user_usergroups = sa.Table(
    'nm_user_usergroups', Base.metadata,
    sa.Column('uid', sa.Integer, sa.ForeignKey('users.id')),
    sa.Column('gid', sa.Integer, sa.ForeignKey('usergroups.id')),
    sa.UniqueConstraint('uid', 'gid')
)

nm_action_roles = sa.Table(
    'nm_action_roles', Base.metadata,
    sa.Column('aid', sa.Integer, sa.ForeignKey('actions.id')),
    sa.Column('rid', sa.Integer, sa.ForeignKey('roles.id')),
    sa.UniqueConstraint('aid', 'rid')
)


class Login(Base):
    """Class to for logins of a user. Attempts to login into the
    application are stored in a table in the database. Each attemp is
    stored with the datetime, the user and the state of the login.

    This information can later be used to give information on suspicious
    logins."""
    __tablename__ = "user_logins"

    id = sa.Column(sa.Integer, primary_key=True)
    datetime = sa.Column(sa.DateTime, default=datetime.utcnow)
    success = sa.Column(sa.Boolean)
    uid = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
    user = sa.orm.relationship("User", backref="logins")

    def __init__(self, user, success):
        self.success = success
        user.logins.append(self)


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

    def create(self, user, values):

        # Delete the gid which sets the default group when creating a
        # new user. The default group when creating a new user is always
        # the usergroup which gets automatically created on user
        # creation. So this value can (and must) be ignored.
        # Not removing the "gid" will otherwise cause an
        # IntegrityError while flushing the new user to the DB as the
        # usergroup with the given id is not persistent in the DB.
        if "gid" in values:
            del values["gid"]
        # Delete the sid which sets the default settings for the same
        # reasons than deleting the "gid" attribute.
        if "sid" in values:
            del values["sid"]

        new_user = BaseFactory.create(self, user, values)

        # Now create a a new Profile
        profile_property = get_prop_from_instance(new_user, "profile",
                                                  include_relations=True)
        profile_class = profile_property.mapper.class_
        profile_factory = BaseFactory(profile_class)
        profile = profile_factory.create(user, {})
        new_user.profile.append(profile)

        # Create settings
        settings_factory = BaseFactory(UserSetting)
        settings = settings_factory.create(user, {})
        new_user.settings = settings

        # A usergroup
        usergroup_property = get_prop_from_instance(new_user, "usergroup",
                                                    include_relations=True)
        usergroup_class = usergroup_property.mapper.class_
        usergroup_factory = BaseFactory(usergroup_class)
        usergroup = usergroup_factory.create(None, {})
        usergroup.name = new_user.login
        usergroup.members.append(new_user)
        # If no default group is set, then set the users group as
        # default group
        new_user.usergroup = values.get("usergroup") or usergroup
        return new_user


class User(BaseItem, Owned, Base):
    __tablename__ = 'users'
    _modul_id = 3
    _sql_eager_loads = ['roles', 'groups', 'profile', 'settings']
    id = sa.Column(sa.Integer, primary_key=True)
    login = sa.Column(sa.String, unique=True, nullable=False)
    password = sa.Column(sa.String, nullable=False)
    activated = sa.Column(sa.Boolean, default=True)
    activation_token = sa.Column(sa.String, nullable=False, default='')
    default_gid = sa.Column(sa.Integer, sa.ForeignKey('usergroups.id'))
    sid = sa.Column(sa.Integer, sa.ForeignKey('user_settings.id'))
    last_login = sa.Column(sa.DateTime)

    # Relations
    profile = sa.orm.relation("Profile", cascade="all, delete-orphan")
    roles = sa.orm.relationship("Role",
                                secondary=nm_user_roles,
                                backref='users')
    groups = sa.orm.relationship("Usergroup",
                                 secondary=nm_user_usergroups,
                                 backref='members')
    usergroup = sa.orm.relationship("Usergroup", uselist=False,
                                    cascade="delete, all",
                                    foreign_keys=[default_gid])
    settings = sa.orm.relationship("UserSetting", uselist=False,
                                   cascade="all,delete")

    @classmethod
    def get_item_factory(cls):
        return UserFactory(cls)

    def has_role(self, role):
        """Return True if the user has the given role. Else False"
        :user: User instance
        :returns: True or False
        """
        roles = [r.name for r in self.roles]
        return role in roles

ADMIN_GROUP_ID = 1
"""Role ID your the system administration group"""
USER_GROUP_ID = 2
"""Role ID your the system user group"""
USER_ROLE_ID = 1
"""Role ID your the system user role"""


class Usergroup(BaseItem, Owned, Base):
    __tablename__ = 'usergroups'
    _modul_id = 4
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, unique=True, nullable=False)
    description = sa.Column(sa.String, nullable=False, default='')

    def __unicode__(self):
        return self.name


class Role(BaseItem, Owned, Base):
    """Roles are used to configure which actions on a specific modul are
    permitted to users. Roles are important during the permission checks
    to determine what the user can so which an item of a certain modul.
    However a role does not determine if the user has access to the item
    at all. This is left to the ownership checks. However a role can be
    configured to be a 'administration role'. This means every user who
    has this role will pass the ownership check during the permission
    checks even if the user is not the owner or in the group of the item
    he wants to.

    The specific actions a user is allowed to do on a item are stored in
    a internal list of ActionsItems. A user will be allowed to call all
    actions assigned to the role he is equipped with.
    """
    __tablename__ = 'roles'
    _modul_id = 5
    id = sa.Column(sa.Integer, primary_key=True)
    label = sa.Column(sa.String, unique=True, nullable=False)
    name = sa.Column(sa.String, unique=True, nullable=False)
    description = sa.Column(sa.Text, nullable=False, default='')
    admin = sa.Column(sa.Boolean, default=False)
    """Flag to set the role as administration role which means that
    the user will gain the assigned permissions irrespective from
    checking the ownership"""

    permissions = sa.orm.relation("ActionItem",
                                  secondary=nm_action_roles,
                                  backref='roles')


class Profile(BaseItem, Owned, Base):
    __tablename__ = 'profiles'
    _modul_id = 6
    id = sa.Column(sa.Integer, primary_key=True)
    first_name = sa.Column(sa.String, nullable=True, default='')
    last_name = sa.Column(sa.String, nullable=True, default='')
    gender = sa.Column(sa.Integer)
    birthday = sa.Column(sa.Date)
    address = sa.Column(sa.Text, nullable=True, default='')
    phone = sa.Column(sa.String, nullable=True, default='')
    email = sa.Column(sa.String, nullable=True)
    web = sa.Column(sa.String, nullable=True, default='')

    # The foreign key to the user is injected from the Owned mixin.
    user = sa.orm.relation("User", cascade="all, delete",
                           single_parent=True,
                           uselist=False)
