import sqlalchemy as sa
from ringo.model import Base
from ringo.model.base import BaseItem
from ringo.model.mixins import Owned, Nested, Meta


class Comment(BaseItem, Meta, Nested, Owned, Base):
    __tablename__ = 'comments'
    _modul_id = 11
    id = sa.Column(sa.Integer, primary_key=True)
    text = sa.Column(sa.Text)
