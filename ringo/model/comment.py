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

    def __unicode__(self):
        return str(self.id)


def init_model(dbsession):
    """Will setup the initial model for the comment.

    :dbsession: Database session to which the items will be added.
    :returns: None
    """
    modul = ModulItem(name='comments')
    modul.clazzpath = "ringo.model.comment.Comment"
    modul.label = "Comment"
    modul.label_plural = "Comments"
    modul.display = "hidden"
    modul.actions.extend(_create_default_actions(dbsession))
    dbsession.add(modul)
