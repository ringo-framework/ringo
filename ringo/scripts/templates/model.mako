import sqlalchemy as sa
from ringo.model import Base
from ringo.model.base import BaseItem, BaseFactory
from ringo.model.modul import ModulItem, _create_default_actions
from ringo.model.mixins import Owned


class ${clazz}Factory(BaseFactory):

    def create(self, user=None):
        new_item = BaseFactory.create(self, user)
        return new_item


class ${clazz}(BaseItem, Owned, Base):
    __tablename__ = '${table}'
    _modul_id = ${id}
    id = sa.Column(sa.Integer, primary_key=True)

    def __unicode__(self):
        return str(self.id)

def init_model(dbsession):
    """Will setup the initial model for the ${modul}.

    :dbsession: Database session to which the items will be added.
    :returns: None
    """
    modul = ModulItem(name='${table}')
    modul.clazzpath = "${clazzpath}"
    modul.label = "${label}"
    modul.label_plural = "${label_plural}"
    modul.display = "header-menu"
    modul.actions.extend(_create_default_actions(dbsession))
    dbsession.add(modul)
