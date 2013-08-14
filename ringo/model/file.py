import sqlalchemy as sa
from ringo.model import Base
from ringo.model.base import BaseItem, BaseFactory
from ringo.model.modul import ModulItem, _create_default_actions
from ringo.model.mixins import Owned


class FileFactory(BaseFactory):

    def create(self, user=None):
        new_item = BaseFactory.create(self, user)
        return new_item


class File(BaseItem, Owned, Base):
    __tablename__ = 'files'
    _modul_id = 8
    id = sa.Column(sa.Integer, primary_key=True)

    def __unicode__(self):
        return str(self.id)

def init_model(dbsession):
    """Will setup the initial model for the file.

    :dbsession: Database session to which the items will be added.
    :returns: None
    """
    modul = ModulItem(name='files')
    modul.clazzpath = "ringo.model.file.File"
    modul.label = "File"
    modul.label_plural = "Files"
    modul.display = "header-menu"
    modul.actions.extend(_create_default_actions(dbsession))
    dbsession.add(modul)
