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
    Table,
    inspect
)

from sqlalchemy.orm import (
    relationship,
    backref,
    attributes
)

from ringo.model import Base
from ringo.lib.helpers import serialize

log = logging.getLogger(__name__)


class Mixin(object):
    """Base mixin class"""

    @classmethod
    def _setup_item_actions(cls):
        return []

    @classmethod
    def get_item_actions(cls, include_super=True):
        """Returns a combined list of actions specific to the mixin and
        base actions. If include_super is false only the actions
        specific to this mixin are returned.

        :include_super: Boolean flag. If true only mixin actions are returned
        :returns: List of ActionItems

        """
        actions = super(Mixin, cls).get_item_actions()
        if not include_super:
            return cls._setup_item_actions()
        return actions + cls._setup_item_actions()

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

    def change_state(self, request, key, old_state_id, new_state_id):
        """Changes the state of the given statemachine from old to new.
        The statemachine is identified by the key in the _statemachines
        dictionary"""
        log.debug("%s -> %s" % (old_state_id, new_state_id))
        sm = self.get_statemachine(key, old_state_id, request)
        sm.set_state(new_state_id)
        # clear cached statemachines
        setattr(self, '_cache_statemachines', {})
        # Add logentry on statechange if the item is loggend
        if isinstance(self, Logged):
            from ringo.model.log import Log
            factory = Log.get_item_factory()
            logentry = factory.create(user=request.user)
            logentry.subject = "State Changed: %s" % self
            self.logs.append(logentry)



    def get_statemachine(self, key, state_id=None, request=None):
        """Returns a statemachine instance for the given key

        :key: Name of the key of the statemachine
        :state_id: initial state of the statemachine
        :returns: Statemachine instance

        """
        if not hasattr(self, '_cache_statemachines'):
            cache = {}
        else:
            cache = getattr(self, '_cache_statemachines')
        if key not in cache:
            cache[key] = self._statemachines[key](self, key, state_id, request)
            setattr(self, '_cache_statemachines', cache)
        else:
            # As the statemachine is cached we need to overwrite the
            # internale _request parameter to have the current request
            # available in the state.
            cache[key]._request = request
        return cache[key]


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

    @declared_attr
    def fid(cls):
        return Column(Integer, ForeignKey('forms.id'))

    @declared_attr
    def form(cls):
        from ringo.model.form import Form
        form = relationship(Form, uselist=False)
        return form

    def get_form_config(self, formname):
        """Return the Configuration for a given form. This function
        overwrites the default get_form_config method from the BaseItem
        to load the configuration from the database. Please take care
        for the inheritance order to enabled overloading of this method."""
        from ringo.model.form import Form
        if self.fid:
            # A reference to a form has been set. Load the references value
            cachename = "%s.%s.%s" % (self.__class__.__name__,
                                      self.fid, formname)
            if not self._cache_form_config.get(cachename):
                factory = Form.get_item_factory()
                form = factory.load(self.fid)
                config = Config(parse(form.definition.encode('utf-8')))
                self._cache_form_config[cachename] = config.get_form(formname)
            return self._cache_form_config[cachename]
        else:
            # Fallback! Should not happen. Load default form.
            return super(Blobform, self).get_form_config(formname)

    def __getattr__(self, name):
        """This function tries to get the given attribute of the item if
        it can not be found using the usual way to get attributes. In
        this case we will split the attribute name by "." and try to get
        the attribute along the "." separated attribute name."""
        data = getattr(self, 'data')
        if data:
            json_data = json.loads(getattr(self, 'data'))
            if json_data.has_key(name):
                return json_data[name]

        element = self
        attributes = name.split('.')
        for attr in attributes:
            element = object.__getattribute__(element, attr)
        return element


    def set_values(self, values):
        """Will set the given values into Blobform items. This function
        overwrites the default behavior of the BaseItem and takes care
        that the data will be saved in the data attribute as JSON
        string."""
        json_data = json.loads(self.get_values().get('data') or "{}")
        columns = self.get_columns(self)
        for key, value in values.iteritems():
            # Ignore private form fields
            if key.startswith('_'):
                continue
            if key in columns:
                log.debug("Setting value '%s' for '%s' in DB" % (value, key))
                setattr(self, key, value)
            else:
                if isinstance(value, datetime.date):
                    value = str(value)
                log.debug("Setting value '%s' for '%s' in JSON" % (value, key))
                json_data[key] = value
        setattr(self, 'data', json.dumps(json_data))

class Version(Base):
    __tablename__ = 'versions'
    id = Column(Integer, primary_key=True)
    values = Column(Text, default=None)
    author = Column(Text, default=None)
    date = Column(DateTime, default=None)

class Versioned(object):
    """Mixin to add version functionallity to a modul. This mixin is
    used to store different "versions" of an item. On each update of
    the item, the serialized values of the item will be saved in the
    version table. Item modul will have a "versions" relationship
    containing all versions of the values for this item."""

    @declared_attr
    def versions(cls):
        tbl_name = "nm_%s_versions" % cls.__name__.lower()
        nm_table = Table(tbl_name, Base.metadata,
                         Column('iid', Integer, ForeignKey(cls.id)),
                         Column('vid', Integer, ForeignKey("versions.id")))
        versions = relationship(Version, secondary=nm_table, cascade="all")
        return versions

    @classmethod
    def create_handler(cls, request, item):
        cls.update_handler(request, item)

    @classmethod
    def update_handler(cls, request, item):
        """Will add the serialized values of the item into the version
        table.

        :request: Current request
        :item: Item handled in the update.

        """
        version = Version()
        values = {}
        item_values = item.get_values(serialized=True)
        version.values = json.dumps(item_values)
        version.author = request.user.login
        version.date = datetime.datetime.now()
        item.versions.append(version)

    def _get_version(self, author, id):
        if not author and not id:
            return self.versions[-2]
        # iterate over the revsersed versions ignoring the last one
        for version in self.versions[-2::-1]:
            if id and version.id == id:
                return version
            elif author and version.author == author:
                return version
        return self.versions[0]

    def get_previous_values(self, author=None, id=None):
        """Returns a dictionary parsed from the last log entry of the
        item containinge the previous values for each field if it has
        been changed."""
        if len(self.versions) < 1:
            return {}
        else:
            pvalues = {}
            last = self._get_version(author, id)
            try:
                values = json.loads(last.values)
                for field in values:
                    if field == "data" and isinstance(self, Blobform):
                        blobdata = json.loads(values[field])
                        for blobfield in blobdata:
                            pvalues[blobfield] = blobdata[blobfield]
                    pvalues[field] = values[field]
            except:
                log.warning(("Could not build previous values dict. "
                             "Maybe old log format?"))
        return pvalues


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
        logs = relationship(Log, secondary=nm_table, cascade="all")
        return logs

    def build_changes(self, old_values, new_values):
        """Returns a dictionary with the old and new values for each
        field which has changed"""
        diff = {}
        if isinstance(self, Blobform):
            data = json.loads(old_values.get("data") or "{}")
            old_values = dict(old_values.items() + data.items())
        for field in new_values:
            oldv = serialize(old_values.get(field))
            newv = serialize(new_values.get(field))
            if newv == oldv:
                continue
            if field == "data":
                diff[field] = {"old": oldv, "new": newv}
            else:
                diff[field] = {"old": serialize(oldv), "new": serialize(newv)}
        return diff

    def add_log_entry(self, subject, text, request):
        """Will add a log entry for the updated item.
        The mapper and the target parameter will be the item which
        iherits this logged mixin.

        :request: Current request
        :subject: Subject of the logentry.
        :text: Text of the logentry.

        """
        from ringo.model.log import Log
        factory = Log.get_item_factory()
        log = factory.create(user=request.user)
        if not subject:
            log.subject = "Update: %s" % self
        else:
            log.subject = subject
        if not text:
            log.text = self._build_changes()
        else:
            log.text = text
        log.author = str(request.user)
        self.logs.append(log)


class Printable(Mixin):

    @classmethod
    def _setup_item_actions(cls):
        from ringo.model.modul import ActionItem
        actions = []
        # Add Print action
        action = ActionItem()
        action.mid = cls.get_item_modul().id
        action.name = 'Print'
        action.url = 'print/{id}'
        action.icon = 'glyphicon glyphicon-print'
        actions.append(action)
        action.permission = 'read'
        action.display = 'secondary'
        return actions


    @declared_attr
    def printtemplates(cls):
        from ringo.model.printtemplate import Printtemplate
        tbl_name = "nm_%s_printtemplates" % cls.__name__.lower()
        nm_table = Table(tbl_name, Base.metadata,
                         Column('iid', Integer, ForeignKey(cls.id)),
                         Column('tid', Integer, ForeignKey("printtemplates.id")))
        logs = relationship(Printtemplate, secondary=nm_table)
        return logs

class Owned(object):
    """Mixin to add references to a user and a usergroup. This
    references are used to build some kind of ownership of the item. The
    ownership is used from the permission system.

    It is posible to configure inhertinace of the owner and group from
    a given parent element. This information is used only while creating
    new instances of the modul. If configured, the default group and
    owner information will be overwritten. This is done at the very end
    of the creation process. See ''save'' method of the BaseItem. You
    can configure the inhertiance by setting the name of the relation to
    the parent item in the ''_inherit_gid'' and ''_inherit_uid'' class
    variable.
    """

    _inherit_gid = None
    """Variable to configure a inheritance of the gid. The variable
    should be the name of the relation to the parent element from which
    the gid will be taken"""
    _inherit_uid = None
    """Variable to configure a inheritance of the uid. The variable
    should be the name of the relation to the parent element from which
    the uid will be taken"""

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
                            backref=backref('parent', remote_side=[cls.id]),
                            cascade="all")

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
        comments = relationship(Comment, secondary=nm_table, cascade="all")
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
        rel = relationship(Todo, secondary=nm_table,
                           backref=clsname+"s", cascade="all")
        return rel
