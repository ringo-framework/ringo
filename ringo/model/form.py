import sqlalchemy as sa
from ringo.model import Base
from ringo.model.base import BaseItem
from ringo.model.statemachine import (
    Statemachine, State,
    null_handler as handler,
    null_condition as condition
)
from ringo.model.mixins import Owned, Meta, StateMixin

d1 = """The form is currently marked as draft. This means it is
currently under work and may change."""
d2 = """The form  is published and can be used in the application. The
form can not be changed."""


class ReviewStatemachine(Statemachine):

    def setup(self):
        s1 = State(self, 1, "Draft", description=d1)
        s2 = State(self, 2, "Published", description=d2)

        s1.add_transition(s2, "Publish", handler, condition)
        s2.add_transition(s1, "Revise", handler, condition)
        return s1


class ReviewStateMixin(StateMixin):
    """Mixin to add Review state functionallity to the Forms"""
    _statemachines = {'review_state_id': ReviewStatemachine}
    review_state_id = sa.Column(sa.Integer, default=1)

    @property
    def review_state(self):
        state = self.get_statemachine('review_state_id')
        return state.get_state()


class Form(BaseItem, ReviewStateMixin, Owned, Meta, Base):
    __tablename__ = 'forms'
    _modul_id = 14
    id = sa.Column(sa.Integer, primary_key=True)
    category = sa.Column(sa.Integer)
    title = sa.Column(sa.String, nullable=True, default='')
    description = sa.Column(sa.Text, nullable=True, default='')
    definition = sa.Column(sa.Text, nullable=True, default='')
    mid = sa.Column(sa.Integer, sa.ForeignKey('modules.id'))

    # relations
    modul = sa.orm.relationship("ModulItem", backref="blobforms")
