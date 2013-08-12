from datetime import date
import sqlalchemy as sa
from ringo.model import Base
from ringo.model.base import BaseItem, BaseFactory, BaseList
from ringo.model.modul import ModulItem, _create_default_actions
from ringo.model.mixins import Owned


class AppointmentFactory(BaseFactory):

    def create(self, user=None):
        new_item = BaseFactory.create(self, user)
        return new_item


class Reminders(BaseList):
    def __init__(self, db, cache=""):
        BaseList.__init__(self, Appointment, db, cache)
        self._filter_appointments()

    def _filter_appointments(self):
        """Will filter out appointments in the past or events which have
        either no or a not mathing reminder"""
        filtered_items = []
        current_date = date.today()
        for item in self.items:
            if item.end < current_date:
                continue
            if (item.reminder
               and abs((current_date - item.start).total_seconds()%60) <= item.reminder):
                filtered_items.append(item)
        self.items = filtered_items

class Appointment(BaseItem, Owned, Base):
    __tablename__ = 'appointments'
    _modul_id = 7
    id = sa.Column(sa.Integer, primary_key=True)

    start = sa.Column('start', sa.Date, nullable=False, default=None)
    end = sa.Column('end', sa.Date, nullable=False, default=None)
    day = sa.Column('day', sa.Text, nullable=True, default=None)
    reminder = sa.Column('reminder', sa.Integer, nullable=True, default=None)
    email = sa.Column('email', sa.Integer, nullable=True, default=None)
    title = sa.Column('title', sa.Text, nullable=False, default=None)
    description = sa.Column('description', sa.Text, nullable=True, default=None)

    def __unicode__(self):
        return str(self.id)

def init_model(dbsession):
    """Will setup the initial model for the appointment.

    :dbsession: Database session to which the items will be added.
    :returns: None
    """
    modul = ModulItem(name='appointments')
    modul.clazzpath = "ringo.model.appointment.Appointment"
    modul.label = "Appointment"
    modul.label_plural = "Appointments"
    modul.display = "header-menu"
    modul.actions.extend(_create_default_actions(dbsession))
    dbsession.add(modul)
