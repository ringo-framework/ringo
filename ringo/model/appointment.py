from datetime import date
import sqlalchemy as sa
from ringo.model import Base
from ringo.model.base import BaseItem, BaseList
from ringo.model.mixins import Owned


class Reminders(BaseList):
    def __init__(self, db, cache=""):
        BaseList.__init__(self, Appointment, db, cache=cache)
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
