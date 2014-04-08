import sqlalchemy as sa
from ringo.model import Base
from ringo.model.base import BaseItem
from ringo.model.mixins import Owned


class File(BaseItem, Owned, Base):
    __tablename__ = 'files'
    _modul_id = 8
    id = sa.Column(sa.Integer, primary_key=True)

    name = sa.Column('name', sa.Text, nullable=True, default=None)
    data = sa.Column('data', sa.LargeBinary, nullable=True, default=None)
    description = sa.Column('description', sa.Text, nullable=True, default=None)
    size = sa.Column('size', sa.Integer, nullable=True, default=None)
    mime = sa.Column('mime', sa.Text, nullable=True, default=None)
