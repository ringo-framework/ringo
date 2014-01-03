import sqlalchemy as sa
from ringo.model import Base
from ringo.model.base import BaseItem, BaseFactory
from ringo.model.modul import ModulItem, _create_default_actions
from ringo.model.mixins import Owned


class TodoFactory(BaseFactory):

    def create(self, user=None):
        new_item = BaseFactory.create(self, user)
        return new_item


class Todo(BaseItem, Owned, Base):
    __tablename__ = 'todos'
    _modul_id = 13
    id = sa.Column(sa.Integer, primary_key=True)

    def __unicode__(self):
        return str(self.id)

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
