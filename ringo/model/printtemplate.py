import sqlalchemy as sa
from ringo.model import Base
from ringo.model.base import BaseItem, BaseFactory
from ringo.model.modul import ModulItem, _create_default_actions, ActionItem
from ringo.model.mixins import Owned


class PrinttemplateFactory(BaseFactory):

    def create(self, user=None):
        new_item = BaseFactory.create(self, user)
        return new_item


class Printtemplate(BaseItem, Owned, Base):
    __tablename__ = 'printtemplates'
    _modul_id = 15
    id = sa.Column(sa.Integer, primary_key=True)
    mid = sa.Column(sa.Integer, sa.ForeignKey('modules.id'))
    name = sa.Column('name', sa.Text, nullable=True, default=None)
    data = sa.Column('data', sa.LargeBinary, nullable=True, default=None)
    description = sa.Column('description', sa.Text, nullable=True, default=None)
    size = sa.Column('size', sa.Integer, nullable=True, default=None)
    mime = sa.Column('mime', sa.Text, nullable=True, default=None)

    # relations
    modul = sa.orm.relationship("ModulItem", backref="printtemplates")

def init_model(dbsession):
    """Will setup the initial model for the printtemplate.

    :dbsession: Database session to which the items will be added.
    :returns: None
    """
    modul = ModulItem(name='printtemplates')
    modul.clazzpath = "ringo.model.printtemplate.Printtemplate"
    modul.label = "Printtemplate"
    modul.label_plural = "Printtemplates"
    modul.display = "admin-menu"
    modul.str_repr = "%s|id"
    modul.actions.extend(_create_default_actions(dbsession))
    dbsession.add(modul)
    # Add download action
    action = ActionItem()
    action.mid = modul.id
    action.name = 'Download'
    action.url = 'download/{id}'
    action.icon = 'icon-download'
    modul.actions.append(action)
