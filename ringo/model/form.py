import sqlalchemy as sa
from ringo.model import Base
from ringo.model.base import BaseItem, BaseFactory
from ringo.model.statemachine import Statemachine, State, \
null_handler as handler, null_condition as condition
from ringo.model.modul import ModulItem, _create_default_actions
from ringo.model.mixins import Owned, Meta, Logged, StateMixin

d1 = """The form is currently marked as draft. This means it is
currently under work and may change."""
d2 = """The form  is marked for a review. This means is work is finished
and the form can not be changed anymore."""
d3 = """The form  is published and can be used in the application. The
form can not be changed."""

class ReviewStatemachine(Statemachine):

    def setup(self):
        s1 = State(self, 1, "Draft", description=d1)
        s2 = State(self, 2, "Review", description=d2)
        s3 = State(self, 3, "Published", description=d3)

        s1.add_transition(s2, "Review", handler, condition)
        s2.add_transition(s1, "Revise", handler, condition)
        s2.add_transition(s3, "Finish", handler, condition)
        s3.add_transition(s1, "Revise", handler, condition)
        return s1

class ReviewStateMixin(StateMixin):
    """Mixin to add Review state functionallity to the Forms"""
    _statemachines = {'review_state_id': ReviewStatemachine}
    review_state_id = sa.Column(sa.Integer, default=1)

    @property
    def review_state(self):
        state = self.get_statemachine('review_state_id')
        return state.get_state()


class FormFactory(BaseFactory):

    def create(self, user=None):
        new_item = BaseFactory.create(self, user)
        return new_item


class Form(BaseItem, ReviewStateMixin, Owned, Meta, Logged, Base):
    __tablename__ = 'forms'
    _modul_id = 14
    id = sa.Column(sa.Integer, primary_key=True)
    category = sa.Column(sa.Integer)
    title = sa.Column(sa.String)
    description = sa.Column(sa.Text)
    definition = sa.Column(sa.Text)

    def __unicode__(self):
        return str(self.id)

def init_model(dbsession):
    """Will setup the initial model for the form.

    :dbsession: Database session to which the items will be added.
    :returns: None
    """
    modul = ModulItem(name='forms')
    modul.clazzpath = "ringo.model.form.Form"
    modul.label = "Form"
    modul.label_plural = "Forms"
    modul.display = "admin-menu"
    modul.actions.extend(_create_default_actions(dbsession))
    dbsession.add(modul)
