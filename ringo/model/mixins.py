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


class Meta(object):
    created = Column(DateTime)
    updated = Column(DateTime)


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
