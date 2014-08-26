from datetime import date, timedelta
from ringo.tests import BaseUnitTest


class ReminderTests(BaseUnitTest):

    def test_reminders(self):
        """Will create some appointments to check the reminder
        functionallity"""
        from ringo.model.appointment import Appointment, get_reminder_list
        factory = Appointment.get_item_factory()
        current_date = date.today()
        yesterday = current_date - timedelta(days=1)
        start = current_date + timedelta(days=1)
        end = start + timedelta(days=1)
        a1 = factory.create(user=None)
        a1.save({"start": yesterday, "end": yesterday, "reminder": 0})
        a2 = factory.create(user=None)
        a2.save({"start": start, "end": end, "reminder": 1})
        a3 = factory.create(user=None)
        a3.save({"start": start, "end": end, "reminder": 1})
        reminders = get_reminder_list(self.request, items=[a1, a2, a3])
        self.assertEqual(len(reminders.items), 2)
