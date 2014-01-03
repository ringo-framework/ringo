import sqlalchemy as sa
from ringo.model import Base
from ringo.model.base import BaseItem, BaseFactory, BaseList
from ringo.model.modul import ModulItem, _create_default_actions
from ringo.model.mixins import Owned, StateMixin
from ringo.model.statemachine import Statemachine, State, null_handler, null_condition


class TodoStatemachine(Statemachine):
    def setup(self):
        s1 = State(self, 1, "New")
        s2 = State(self, 2, "In Progress")
        s3 = State(self, 3, "Done")

        s1.add_transition(s2, "Start", null_handler, null_condition)
        s2.add_transition(s3, "Resolve", null_handler, null_condition)
        s3.add_transition(s2, "Reopen", null_handler, null_condition)
        return s1

class TodoStateMixin(StateMixin):
        _statemachines = {'todo_state_id': TodoStatemachine}
        # Configue a field in the model which saves the current
        # state per state machine
        todo_state_id = sa.Column(sa.Integer, default=1)

        # Optional. Create a property to access the statemachine
        # like an attribute. This gets usefull if you want to access
        # the state in overview lists.
        @property
        def todo_state(self):
            state = self.get_statemachine('todo_state_id')
            return state.get_state()


class TodoFactory(BaseFactory):
    """Factory to create todo items. The factory will create todo items
    with the user group set to "users" by default. This ensures that
    todo items are basically editable by all users in the system."""

    def create(self, user=None):
        new_item = BaseFactory.create(self, user)
        new_item.gid = 2 # Set groupid to "users"
        new_item.assigned.append(user)
        return new_item

class TodoList(BaseList):
    """The TodoList will list all the todo elements which are 1. accessable
    by the user and 2. are assigned to the current user. Users in the role
    "admin" will of course get all todo items"""

    def _filter_for_user(self, items, user):
        """Filter out todo elements which are not assinged to the user"""
        items = BaseList._filter_for_user(self, items, user)
        # Now filter out all the todo items which are not assinged to
        # the current user.
        if user is not None and user.has_role('admin'):
            return items
        elif user is not None:
            filtered_items = []
            for item in items:
                if user.id in [u.id for u in item.assigned]:
                    filtered_items.append(item)
            return filtered_items
        return items

nm_todo_users = sa.Table(
    'nm_todo_users', Base.metadata,
    sa.Column('uid', sa.Integer, sa.ForeignKey('users.id')),
    sa.Column('tid', sa.Integer, sa.ForeignKey('todos.id'))
)

class Todo(BaseItem, Owned, TodoStateMixin, Base):
    __tablename__ = 'todos'
    _modul_id = 13
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column('name', sa.Text, nullable=True, default=None)
    deadline = sa.Column('deadline', sa.DateTime, default=None)
    reminder = sa.Column('reminder', sa.Integer, default=None)
    reminddate = sa.Column('reminddate', sa.DateTime, default=None)
    priority = sa.Column('priority', sa.Integer, default=None)
    description = sa.Column('description', sa.Text, default=None)

    assigned_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    assigned = sa.orm.relationship("User", secondary=nm_todo_users)

    def __unicode__(self):
        return str(self.id)

    @classmethod
    def get_item_factory(cls):
        return TodoFactory(cls)

    @classmethod
    def get_item_list(cls, request, user=None, cache=None):
        return TodoList(cls, request, user, cache=None)

def init_model(dbsession):
    """Will setup the initial model for the todo.

    :dbsession: Database session to which the items will be added.
    :returns: None
    """
    modul = ModulItem(name='todos')
    modul.clazzpath = "ringo.model.todo.Todo"
    modul.label = "Todo"
    modul.label_plural = "Todos"
    modul.display = "hidden"
    modul.actions.extend(_create_default_actions(dbsession))
    dbsession.add(modul)
