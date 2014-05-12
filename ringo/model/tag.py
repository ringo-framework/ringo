import sqlalchemy as sa
from ringo.model import Base
from ringo.model.base import BaseItem
from ringo.model.mixins import Owned


class Tag(BaseItem, Owned, Base):
    """Tags (keywords) can be used to mark items."""
    __tablename__ = 'tags'
    _modul_id = 12
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column('name', sa.Text, default=None)
    description = sa.Column('description', sa.Text, default=None)
    tagtype = sa.Column('type', sa.Integer, default=None)

    # Relation to a modul. Tags can be assigned to a module for
    # filtering.
    mid = sa.Column(sa.Integer, sa.ForeignKey('modules.id'))
    modul = sa.orm.relationship("ModulItem", backref="tags")

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
