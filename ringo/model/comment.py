import sqlalchemy as sa
from ringo.model import Base
from ringo.model.base import BaseItem, BaseFactory
from ringo.model.modul import ModulItem, _create_default_actions
from ringo.model.mixins import Owned, Nested, Meta


class CommentFactory(BaseFactory):

    def create(self, user=None):
        new_item = BaseFactory.create(self, user)
        return new_item


class Comment(BaseItem, Meta, Nested, Owned, Base):
    __tablename__ = 'comments'
    _modul_id = 11
    id = sa.Column(sa.Integer, primary_key=True)
    text = sa.Column(sa.Text)
