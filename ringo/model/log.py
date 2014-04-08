import sqlalchemy as sa
from ringo.model import Base
from ringo.model.base import BaseItem
from ringo.model.mixins import Owned, Meta


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
