from datetime import date

from todoms.attributes import RecurrenceRangeType
from todoms.recurrence.ranges import BaseRecurrenceRange, EndDate, NoEnd, Numbered

# API doesn't really support ranges. The start date has to be set as the due date
# of the task. The end date is not supported at all.


def test_base_range_to_dict():
    range = BaseRecurrenceRange(
        _range_type=RecurrenceRangeType.END_DATE, start_date=date(2020, 4, 8)
    )

    assert range.to_dict() == {"type": "endDate"}


def test_end_date_to_dict():
    range = EndDate(
        start_date=date(2020, 4, 8),
        end_date=date(2022, 4, 8),
    )

    assert range.to_dict() == {
        "type": "endDate",
    }


def test_no_end_to_dict():
    range = NoEnd(start_date=date(2020, 4, 8))

    assert range.to_dict() == {"type": "noEnd"}


def test_numbered_to_dict():
    range = Numbered(start_date=date(2020, 4, 8), occurrences=120)

    assert range.to_dict() == {
        "type": "numbered",
        "numberOfOccurrences": 120,
    }
