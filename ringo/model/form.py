import sqlalchemy as sa
from ringo.model import Base
from ringo.model.base import BaseItem, BaseFactory
from ringo.model.modul import ModulItem, _create_default_actions
from ringo.model.mixins import Owned, Meta, Logged


class FormFactory(BaseFactory):

    def create(self, user=None):
        new_item = BaseFactory.create(self, user)
        return new_item


class Form(BaseItem, Owned, Meta, Logged, Base):
    __tablename__ = 'forms'
    _modul_id = 11
    id = sa.Column(sa.Integer, primary_key=True)
    category = sa.Column(sa.Integer, nullable=False)
    title = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.Text)
    definition = sa.Column(sa.Text)

    def __unicode__(self):
        return str(self.id)

def init_model(dbsession):
    """Will setup the initial model for the form.

    :dbsession: Database session to which the items will be added.
    :returns: None
    """
    modul = ModulItem(name='forms')
    modul.clazzpath = "ringo.model.form.Form"
    modul.label = "Form"
    modul.label_plural = "Forms"
    modul.display = "admin-menu"
    modul.actions.extend(_create_default_actions(dbsession))
    dbsession.add(modul)
