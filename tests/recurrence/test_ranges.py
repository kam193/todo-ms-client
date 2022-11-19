from datetime import date

from todoms.attributes import RecurrenceRangeType
from todoms.recurrence.ranges import BaseRecurrenceRange, EndDate, NoEnd, Numbered


def test_base_range_to_dict():
    range = BaseRecurrenceRange(
        _range_type=RecurrenceRangeType.END_DATE, start_date=date(2020, 4, 8)
    )

    assert range.to_dict() == {"type": "endDate", "startDate": "2020-04-08"}


def test_end_date_to_dict():
    range = EndDate(
        start_date=date(2020, 4, 8),
        end_date=date(2022, 4, 8),
    )

    assert range.to_dict() == {
        "type": "endDate",
        "startDate": "2020-04-08",
        "endDate": "2022-04-08",
    }


def test_no_end_to_dict():
    range = NoEnd(start_date=date(2020, 4, 8))

    assert range.to_dict() == {"type": "noEnd", "startDate": "2020-04-08"}


def test_numbered_to_dict():
    range = Numbered(start_date=date(2020, 4, 8), occurrences=120)

    assert range.to_dict() == {
        "type": "numbered",
        "startDate": "2020-04-08",
        "numberOfOccurrences": 120,
    }
