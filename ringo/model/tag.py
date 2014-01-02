import sqlalchemy as sa
from ringo.model import Base
from ringo.model.base import BaseItem, BaseFactory
from ringo.model.modul import ModulItem, _create_default_actions
from ringo.model.mixins import Owned


class TagFactory(BaseFactory):

    def create(self, user=None):
        new_item = BaseFactory.create(self, user)
        return new_item


class Tag(BaseItem, Owned, Base):
    """Tags (keywords) can be used to mark items."""
    __tablename__ = 'tags'
    _modul_id = 12
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column('name', sa.Text, default=None)
    description = sa.Column('description', sa.Text, default=None)
    tagtype = sa.Column('type', sa.Integer, default=None)

    def render(self):
        mapping = {
            0: "label label-default",
            1: "label label-prinary",
            2: "label label-success",
            3: "label label-info",
            4: "label label-warning",
            5: "label label-danger"}
        return '<span class="%s">%s</span>' % (mapping.get(self.tagtype),
                                               self.name)

    def __unicode__(self):
        return self.name


def init_model(dbsession):
    """Will setup the initial model for the tag.

    :dbsession: Database session to which the items will be added.
    :returns: None
    """
    modul = ModulItem(name='tags')
    modul.clazzpath = "ringo.model.tag.Tag"
    modul.label = "Tag"
    modul.label_plural = "Tags"
    modul.display = "admin-menu"
    modul.actions.extend(_create_default_actions(dbsession))
    dbsession.add(modul)
