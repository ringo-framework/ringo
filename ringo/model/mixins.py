"""
Mixins can be used to add certain functionality to the items of a
module.  Mixins are used in multiple inheritance. The mixin ensures that
the item will have all needed fields in the database and provides the
proper interface to use the added functionality. Example::

        class Comment(BaseItem, Nested, Meta, Owned, Base):
            __tablename__ = 'comments'
            _modul_id = 99
            id = sa.Column(sa.Integer, primary_key=True)
            comment = sa.Column('comment', sa.Text)

            ...

The comment class in the example only defines the two fields `id` and
`comment`. But as it inherits from :ref:`mixin_nested`, :ref:`mixin_meta` and
:ref:`mixin_owned` it also will have date fields with the creation and date of
the last update, references to the user and group which ownes the Comment.
Further the 'Nested' mixin will ensure the comments can reference each other
to be able to build a hierarchy structure (e.g Threads in the example of the
comments).

.. important::

    As most of the mixins will add additional tables and database fields
    to your item it is needed to migrate your database to the new model.
    See :ref:`alembic_migration` section for more information.
"""
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
    backref,
    attributes
)

from ringo.model import Base

log = logging.getLogger(__name__)


class StateMixin(object):
    """Mixin to add one or more Statemachines to an item.  The
    statemachines are stored in a internal '_statemachines' dictionary.
    The current state is stored as integer value per item. This field
    must be created manually.  The name of the field which stores the
    value for the current state must be the keyname of the
    '_statemachines' dictionary.

    Example Mixin usage::

        class FooMixin(StateMixin):
            # Mixin inherited from the StateMixin to add the Foobar
            # state machine

            # Attach the statemachines to an internal dictionary
            _statemachines = {'foo_state_id': FooStatemachine}

            # Configue a field in the model which saves the current
            # state per state machine
            foo_state_id = sa.Column(sa.Integer, default=1)

            # Optional. Create a property to access the statemachine
            # like an attribute. This gets usefull if you want to access
            # the state in overview lists.
            @property
            def foo_state(self):
                state = self.get_statemachine('foo_state_id')
                return state.get_state()
    """

    """Mapping of statemachines to attributes. The key in the dictionary
    must be the name of the field which stores the integer value of the
    current state of the statemachine."""
    _statemachines = {}

    @classmethod
    def list_statemachines(cls):
        """Returns a list keys of configured statemachines"""
        return cls._statemachines.keys()

    def get_statemachine(self, key):
        """Returns a statemachine instance for the given key

        :key: Name of the key of the statemachine
        :returns: Statemachine instance

        """
        return self._statemachines[key](self, key)


class Meta(object):
    """Mixin to add a created and a updated datefield to items. The
    updated datefield will be updated on every update of the item with
    the datetime of the update."""
    created = Column(DateTime, default=datetime.datetime.utcnow)
    updated = Column(DateTime, default=datetime.datetime.utcnow)

    @classmethod
    def update_handler(cls, request, item):
        """Will update the updated attribute to the current datetime.
        The mapper and the target parameter will be the item which
        iherits this meta mixin.

        :request: Current request
        :item: Item handled in the update.

        """
        item.updated = datetime.datetime.now()


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

    def _build_changes(self, allfields=False):
        diff = []
        for field in self.get_columns(include_relations=True):
            history = attributes.get_history(self, field)
            try:
                newv = history[0][0]
            except IndexError:
                newv = ""
            try:
                curv = history[1][0]
            except IndexError:
                curv = ""
            try:
                oldv = history[2][0]
            except IndexError:
                oldv = ""

            if newv:
                diff.append('%s: "%s" -> "%s"' % (field, oldv, newv))
            elif allfields:
                diff.append('%s: "%s"' % (field, curv))
        return "\n".join(diff)

    @classmethod
    def create_handler(cls, request, item):
        subject = "Create: %s" % item
        text = item._build_changes(allfields=True)
        cls.update_handler(request, item, subject, text)

    @classmethod
    def update_handler(cls, request, item, subject=None, text=None):
        """Will add a log entry for the updated item.
        The mapper and the target parameter will be the item which
        iherits this logged mixin.

        :request: Current request
        :item: Item handled in the update.
        :subject: Subject of the logentry.
        :text: Text of the logentry.

        """
        from ringo.model.log import Log
        factory = Log.get_item_factory()
        log = factory.create(user=None)
        if not subject:
            log.subject = "Update: %s" % item
        else:
            log.subject = subject
        if not text:
            log.text = item._build_changes()
        else:
            log.text = text
        log.uid = request.user.id
        log.gid = request.user.gid
        log.author = str(request.user)
        item.logs.append(log)


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
