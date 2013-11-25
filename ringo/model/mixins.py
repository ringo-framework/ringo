import datetime
from sqlalchemy.ext.declarative import declared_attr

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
)

from sqlalchemy.orm import (
    relationship,
    backref
)

class StateMixin(object):
    """Mixin to add one or more Statemachines to an item.  The
    statemachines are stored in a internal '_statemachines' dictionary.
    The current state is stored as integer value per item. This field
    must be created manually.  The name of the field which stores the
    value for the current state must be the keyname of the
    '_statemachines' dictionary."""

    """Mapping of statemachines to attributes. The key in the dictionary
    must be the name of the field which stores the integer value of the
    current state of the statemachine."""
    _statemachines = {}

    @classmethod
    def list_statemachines(cls):
        """Returns a list keys of configured statemachines"""
        return self._statemachines.keys()


    def get_statemachine(self, key):
        """Returns a statemachine instance for the given key

        :key: Name of the key of the statemachine
        :returns: Statemachine instance

        """
        return self._statemachines[key](self, key)


class Meta(object):
    created = Column(DateTime, default=datetime.datetime.utcnow)
    updated = Column(DateTime, default=datetime.datetime.utcnow)


class Owned(object):

    @declared_attr
    def uid(cls):
        return Column(Integer, ForeignKey('users.id'))

    @declared_attr
    def owner(cls):
        return relationship("User",
                            primaryjoin="User.id==%s.uid" % cls.__name__)

    @declared_attr
    def gid(cls):
        return Column(Integer, ForeignKey('usergroups.id'))

    @declared_attr
    def group(cls):
        return relationship("Usergroup",
                            primaryjoin="Usergroup.id==%s.gid" % cls.__name__)

    def is_owner(self, user):
        """Returns true if the Item is owned by the given user."""
        return user.id == self.uid


class Nested(object):
    """Mixin to make nested (self-reference) Items possible. Each item
    can have a parent item and many children. The class will add two
    relation attribute to the inheriting class. The parent item is
    available under the *parent* attribute. The children items are
    available under the *children* attribute."""

    @declared_attr
    def parent_id(cls):
        name = "%s.id" % cls.__tablename__
        return Column(Integer, ForeignKey(name))

    @declared_attr
    def children(cls):
        name = cls.__name__
        join = "%s.id==%s.parent_id" % (name, name)
        return relationship(name,
                            primaryjoin=join,
                            backref=backref('parent', remote_side=[cls.id]))
