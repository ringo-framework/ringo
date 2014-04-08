import sqlalchemy as sa
from ringo.model import Base
from ringo.model.base import BaseItem
from ringo.model.mixins import Owned


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
