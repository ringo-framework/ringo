import sqlalchemy as sa
from ringo.model import Base
from ringo.model.base import BaseItem
from ringo.model.mixins import Owned


class ${clazz}(BaseItem, Owned, Base):
    __tablename__ = '${table}'
    _modul_id = ${id}
    id = sa.Column(sa.Integer, primary_key=True)
