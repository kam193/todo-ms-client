from datetime import date, datetime

from todoms import recurrence
from todoms.convertable import BaseConvertableFieldsObject
from todoms.fields.recurrence import DueDatetime, RecurrenceField


class DummyResource(BaseConvertableFieldsObject):
    recurrence = RecurrenceField("recurrence")
    due_datetime = DueDatetime("dueDateTime")


class TestDueDatetimeField:
    def test_duedatetime_uses_own_value(self):
        obj = DummyResource()
        obj.due_datetime = datetime(2020, 1, 1, 0, 0, 0)
        obj.recurrence = recurrence.Recurrence(
            recurrence.patterns.Daily(interval=1),
            recurrence.ranges.NoEnd(start_date=datetime(2021, 1, 1, 0, 0, 0)),
        )

        assert obj.due_datetime == datetime(2020, 1, 1, 0, 0, 0)

    def test_duedatetime_falls_back_to_recurrence_when_empty(self):
        obj = DummyResource()
        obj.recurrence = recurrence.Recurrence(
            recurrence.patterns.Daily(interval=1),
            recurrence.ranges.NoEnd(start_date=date(2021, 1, 1)),
        )

        assert obj.due_datetime == datetime(2021, 1, 1, 0, 0, 0)
        dict_form = obj.to_dict()
        assert dict_form["dueDateTime"] is not None

    def test_duedatetime_uses_datetime_from_recurrence_when_empty(self):
        obj = DummyResource()
        obj.recurrence = recurrence.Recurrence(
            recurrence.patterns.Daily(interval=1),
            recurrence.ranges.NoEnd(start_date=datetime(2021, 1, 1, 12, 0, 0)),
        )

        assert obj.due_datetime == datetime(2021, 1, 1, 12, 0, 0)
        dict_form = obj.to_dict()
        assert dict_form["dueDateTime"] is not None
