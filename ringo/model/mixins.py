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
import json
import logging
from formbar.config import Config, parse
from sqlalchemy.ext.declarative import declared_attr

from sqlalchemy import (
    Column,
    Text,
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

class Blobform(object):
    """Mixin to add a data fields to store form data as JSON in a single
    field. Further the fid references the form definiton. The mixin will
    overwrite the way how to get the form definiton and how to get
    values from the item."""
    data = Column(Text, default="{}")
    _form_id = 1

    @declared_attr
    def fid(cls):
        return Column(Integer, ForeignKey('forms.id'))

    @declared_attr
    def form(cls):
        from ringo.model.form import Form
        form = relationship(Form, uselist=False)
        return form

    @classmethod
    def get_form_config(cls, formname):
        """Return the Configuration for a given form. This function
        overwrites the default get_form_config method from the BaseItem
        to load the configuration from the database. Please take care
        for the inheritance order to enabled overloading of this method."""
        from ringo.model.form import Form
        factory = Form.get_item_factory()
        form = factory.load(cls._form_id)
        cachename = "%s.%s.%s" % (cls.__name__, form.id, formname)
        if not cls._cache_form_config.get(cachename):
            config = Config(parse(form.definition.encode('utf-8')))
            cls._cache_form_config[cachename] = config.get_form(formname)
        return cls._cache_form_config[cachename]

    def __getattr__(self, name):
        """This function tries to get the given attribute of the item if
        it can not be found using the usual way to get attributes. In
        this case we will split the attribute name by "." and try to get
        the attribute along the "." separated attribute name."""
        json_data = json.loads(getattr(self, 'data'))
        if json_data.has_key(name):
            return json_data[name]

        element = self
        attributes = name.split('.')
        for attr in attributes:
            element = object.__getattribute__(element, attr)
        return element

    def save(self, data, dbsession=None):
        """Will save the given data into Blobform items. This function
        overwrites the default behavior of the BaseItem and takes care
        that the data will be saved in the data attribute as JSON
        string. If the current item has no value for the id attribute it
        is assumed that this item must be added to the database as a new
        item. In this case you need to provide a dbsession as the new
        item is not linked to any dbsession yet.

        Please note, that you must ensure that the submitted values are
        validated. This function does no validation on the submitted
        data.

        :data: Dictionary with key value pairs.
        :dbsession: Current db session. Used when saving new items.
        :returns: item with new data.

        """
        json_data = {}
        columns = self.get_columns(self)
        for key, value in data.iteritems():
            if key in columns:
                setattr(self, key, value)
            else:
                if isinstance(value, datetime.date):
                    value = str(value)
                json_data[key] = value
        setattr(self, 'data', json.dumps(json_data))

        # If the item has no id, then we assume it is a new item. So
        # add it to the database session.
        if not self.id and dbsession:
            dbsession.add(self)
        return self



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


class Commented(object):
    """Mixin to add comment functionallity to a modul. Adding this Mixin
    the item of a modul will have a "comments" relationship containing all
    the comment entries for this item."""

    @declared_attr
    def comments(cls):
        from ringo.model.comment import Comment
        tbl_name = "nm_%s_comments" % cls.__name__.lower()
        nm_table = Table(tbl_name, Base.metadata,
                         Column('iid', Integer, ForeignKey(cls.id)),
                         Column('cid', Integer, ForeignKey("comments.id")))
        comments = relationship(Comment, secondary=nm_table)
        return comments

    @classmethod
    def create_handler(cls, request, item):
        cls.update_handler(request, item)

    @classmethod
    def update_handler(cls, request, item):
        """Will add a comment entry for the updated item if the request
        contains a parameter 'comment'.  The mapper and the target
        parameter will be the item which inherits this commented mixin.

        :request: Current request
        :item: Item handled in the update.
        """
        from ringo.model.comment import Comment
        log.debug("Called update_handler for %s" % cls)
        user_comment = request.params.get('comment')
        if user_comment:
            factory = Comment.get_item_factory()
            comment = factory.create(request.user)
            comment.text = user_comment
            item.comments.append(comment)
        return item


class Tagged(object):
    """Mixin to add tag (keyword) functionallity to a modul. Adding this Mixin
    the item of a modul will have a "tags" relationship containing all
    the tag entries for this item."""

    @declared_attr
    def tags(cls):
        from ringo.model.tag import Tag
        tbl_name = "nm_%s_tags" % cls.__name__.lower()
        nm_table = Table(tbl_name, Base.metadata,
                         Column('iid', Integer, ForeignKey(cls.id)),
                         Column('tid', Integer, ForeignKey("tags.id")))
        tags = relationship(Tag, secondary=nm_table)
        return tags


class Todo(object):
    """Mixin to add todo functionallity to a modul. Adding this Mixin
    the item of a modul will have a "todo" relationship containing all
    the todo entries for this item."""

    @declared_attr
    def todo(cls):
        from ringo.model.todo import Todo
        clsname = cls.__name__.lower()
        tbl_name = "nm_%s_todos" % clsname
        nm_table = Table(tbl_name, Base.metadata,
                         Column('iid', Integer, ForeignKey(cls.id)),
                         Column('tid', Integer, ForeignKey("todos.id")))
        rel = relationship(Todo, secondary=nm_table, backref=clsname+"s")
        return rel
