import datetime
import logging
from sqlalchemy.ext.declarative import declared_attr

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    Table
)

from sqlalchemy.orm import (
    relationship,
    backref
)

from ringo.model import Base

log = logging.getLogger(__name__)


class Meta(object):
    """Mixin to add a created and a updated datefield to items. The
    updated datefield will be updated on every update of the item with
    the datetime of the update."""
    created = Column(DateTime, default=datetime.datetime.utcnow)
    # TODO: Make sure that the updated attribute gets updated on every
    # update. (torsten) <2013-10-07 18:00>
    updated = Column(DateTime, default=datetime.datetime.utcnow)

    @classmethod
    def before_update_event_listener(cls, mapper, connection, target):
        """Will update the updated attribute to the current datetime.
        The mapper and the target parameter will be the item which
        iherits this meta mixin.

        :mapper: Mapper item for the target class
        :connection: Current connection
        :target: Target class.

        """
        target.updated = datetime.datetime.now()


class Logged(object):
    """Mixin to add logging functionallity to a modul. Adding this Mixin
    the item of a modul will have a "logs" relationship containing all
    the log entries for this item. Log entries can be created
    automatically by the system or may be created manual by the user.
    Manual log entries. Needs to be configured (Permissions)"""


    @declared_attr
    def logs(cls):
        from ringo.model.log import Log
        tbl_name = "nm_%s_logs" % cls.__name__.lower()
        nm_table = Table(tbl_name, Base.metadata,
                         Column('iid', Integer, ForeignKey(cls.id)),
                         Column('lid', Integer, ForeignKey("logs.id")))
        logs = relationship(Log, secondary=nm_table)
        return logs

    @classmethod
    def before_update_event_listener(cls, mapper, connection, target):
        """Will add a log entry for the updated item.
        The mapper and the target parameter will be the item which
        iherits this logged mixin.

        :mapper: Mapper item for the target class
        :connection: Current connection
        :target: Target class.

        """
        from ringo.model.log import Log
        factory = Log.get_item_factory()
        log = factory.create(user=None)
        log.subject = "Update: %s" % target
        target.logs.append(log)
        print target.logs


class Owned(object):
    """Mixin to add references to a user and a usergroup. This
    references are used to build some kind of ownership of the item. The
    ownership is used from the permission system."""

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

    def get_parents(self):
        """Return a list of all parents of the current item
        :returns: List of BaseItems

        """
        parents = []
        if not self.parent_id:
            return parents
        else:
            parents.append(self.parent)
            parents.extend(self.parent.get_parents())
        return parents

    def get_children(self):
        """Returns a list of all children und subchildren
        :returns: List of BaseItems

        """
        childs = []
        for child in self.children:
            childs.append(child)
            childs.extend(child.get_children())
        return childs
