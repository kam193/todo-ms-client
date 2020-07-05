from datetime import datetime

from dateutil import tz

from todoms.attributes import RecurrenceRangeType
from todoms.recurrence.ranges import BaseRecurrenceRange, EndDate, NoEnd, Numbered


def test_base_range_to_dict():
    range = BaseRecurrenceRange(
        RecurrenceRangeType.END_DATE, start_date=datetime(2020, 4, 8, 16, tzinfo=tz.UTC)
    )

    assert range.to_dict() == {"type": "endDate", "startDate": "2020-04-08T16:00:00Z"}


def test_end_date_to_dict():
    range = EndDate(
        start_date=datetime(2020, 4, 8, 16, tzinfo=tz.UTC),
        end_date=datetime(2022, 4, 8, 16, tzinfo=tz.UTC),
    )

    assert range.to_dict() == {
        "type": "endDate",
        "startDate": "2020-04-08T16:00:00Z",
        "endDate": "2022-04-08T16:00:00Z",
    }


def test_no_end_to_dict():
    range = NoEnd(start_date=datetime(2020, 4, 8, 16, tzinfo=tz.UTC))

    assert range.to_dict() == {"type": "noEnd", "startDate": "2020-04-08T16:00:00Z"}


def test_numbered_to_dict():
    range = Numbered(
        start_date=datetime(2020, 4, 8, 16, tzinfo=tz.UTC), occurrences=120
    )

    assert range.to_dict() == {
        "type": "numbered",
        "startDate": "2020-04-08T16:00:00Z",
        "numberOfOccurrences": 120,
    }
