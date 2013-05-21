import sqlalchemy as sa
from ringo.model import Base
from ringo.model.base import BaseItem, BaseFactory
from ringo.model.mixins import Owned


class $modul_clazzFactory(BaseFactory):

    def create(self, user=None):
        new_item = BaseFactory.create(self, user)
        return new_user

class $modul_clazz(BaseItem, Owned, Base):
    __tablename__ = '$modul'
    _modul_id = $modul_id
    id = sa.Column(sa.Integer, primary_key=True)

    # Configuration
    _table_fields = [('id', 'ID')]

    def __unicode__(self):
        return self.id
