from datetime import date
import sqlalchemy as sa
from ringo.model import Base
from ringo.model.base import BaseItem, get_item_list
from ringo.model.mixins import Owned


def get_reminder_list(request, user=None, cache="", items=None):
    baselist = get_item_list(request, Appointment, user, cache, items)
    filtered_items = []
    current_date = date.today()
    for item in baselist.items:
        if item.end < current_date:
            continue
        if (item.reminder
           and abs((current_date - item.start).total_seconds() % 60) <= item.reminder):
            filtered_items.append(item)
    baselist.items = filtered_items
    return baselist


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
