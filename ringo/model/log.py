import sqlalchemy as sa
from ringo.model import Base
from ringo.model.base import BaseItem, BaseFactory
from ringo.model.modul import ModulItem, _create_default_actions
from ringo.model.mixins import Owned, Meta


class LogFactory(BaseFactory):

    def create(self, user=None):
        new_item = BaseFactory.create(self, user)
        return new_item


class Log(BaseItem, Owned, Meta, Base):
    __tablename__ = 'logs'
    _modul_id = 10
    id = sa.Column(sa.Integer, primary_key=True)
    author = sa.Column('author', sa.Text, nullable=True, default=None)
    """Textual representation of the user. This will even stay if the
    origin creator (user) is deleted."""
    category = sa.Column('category', sa.Integer, nullable=True, default=None)
    subject = sa.Column('subject', sa.Text, nullable=False, default=None)
    text = sa.Column('text', sa.Text, nullable=True, default=None)

    def __unicode__(self):
        return str(self.id)

def init_model(dbsession):
    """Will setup the initial model for the log.

    :dbsession: Database session to which the items will be added.
    :returns: None
    """
    modul = ModulItem(name='logs')
    modul.clazzpath = "ringo.model.log.Log"
    modul.label = "Log"
    modul.label_plural = "Logs"
    modul.display = "admin-menu"
    modul.actions.extend(_create_default_actions(dbsession))
    dbsession.add(modul)
