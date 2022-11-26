from datetime import date

import pytest

from todoms.converters.recurrence import (
    RecurrenceConverter,
    RecurrencePatternConverter,
    RecurrenceRangeConverter,
)
from todoms.recurrence import Recurrence, patterns, ranges


class TestRecurrencePatternConverter:
    @pytest.mark.parametrize(
        "data,expected_class",
        [
            ({"type": "daily", "interval": 3}, patterns.Daily),
            (
                {
                    "type": "weekly",
                    "interval": 6,
                    "daysOfWeek": ["monday", "friday"],
                    "firstDayOfWeek": "sunday",
                },
                patterns.Weekly,
            ),
            (
                {"type": "absoluteMonthly", "interval": 3, "dayOfMonth": 15},
                patterns.MonthlyAbsolute,
            ),
            (
                {
                    "type": "relativeMonthly",
                    "interval": 3,
                    "daysOfWeek": ["friday", "saturday"],
                },
                patterns.MonthlyRelative,
            ),
            (
                {
                    "type": "absoluteYearly",
                    "interval": 1,
                    "dayOfMonth": 17,
                    "month": 6,
                },
                patterns.YearlyAbsolute,
            ),
            (
                {
                    "type": "relativeYearly",
                    "interval": 2,
                    "daysOfWeek": ["monday", "thursday"],
                    "month": 3,
                },
                patterns.YearlyRelative,
            ),
        ],
    )
    def test_recurrence_patterns_converter(self, data, expected_class):
        converter = RecurrencePatternConverter()
        assert isinstance(converter.obj_converter(data), expected_class) is True

    def test_recurrence_patterns_converter_when_invalid(self):
        converter = RecurrencePatternConverter()
        with pytest.raises(ValueError):
            converter.obj_converter({"type": "some invalid"})

    def test_recurrence_patterns_converter_when_none(self):
        converter = RecurrencePatternConverter()
        assert converter.obj_converter(None) is None

    def test_recurrence_pattern_back_converter(self):
        converter = RecurrencePatternConverter()
        data = patterns.Daily(interval=3)

        assert converter.back_converter(data) == {"type": "daily", "interval": 3}

    def test_recurrence_pattern_back_converter_when_none(self):
        converter = RecurrencePatternConverter()
        assert converter.back_converter(None) is None


class TestRecurrenceRangeConverter:
    @pytest.mark.parametrize(
        "data,expected_class",
        [
            (
                {
                    "type": "endDate",
                    "startDate": "2020-04-08T16:00:00Z",
                    "endDate": "2022-04-08T16:00:00Z",
                },
                ranges.EndDate,
            ),
            ({"type": "noEnd", "startDate": "2020-04-08T16:00:00Z"}, ranges.NoEnd),
            (
                {
                    "type": "numbered",
                    "startDate": "2020-04-08T16:00:00Z",
                    "numberOfOccurrences": 120,
                },
                ranges.Numbered,
            ),
        ],
    )
    def test_recurrence_range_converter(self, data, expected_class):
        converter = RecurrenceRangeConverter()
        assert isinstance(converter.obj_converter(data), expected_class) is True

    def test_recurrence_range_converter_when_invalid(self):
        converter = RecurrenceRangeConverter()
        with pytest.raises(ValueError):
            converter.obj_converter({"type": "invalid"})

    def test_recurrence_range_converter_when_none(self):
        converter = RecurrenceRangeConverter()
        assert converter.obj_converter(None) is None

    def test_recurrence_range_back_converter(self):
        converter = RecurrenceRangeConverter()
        data = ranges.EndDate(
            start_date=date(2020, 4, 8),
            end_date=date(2022, 4, 8),
        )
        # API requires omitting dates, see #104
        assert converter.back_converter(data) == {
            "type": "endDate",
        }

    def test_recurrence_range_back_converter_when_none(self):
        converter = RecurrenceRangeConverter()
        assert converter.back_converter(None) is None


class TestRecurrenceConverter:
    def test_recurrence_converter(self):
        converter = RecurrenceConverter()

        data = {
            "pattern": {
                "type": "absoluteYearly",
                "interval": 1,
                "month": 7,
                "dayOfMonth": 5,
                "firstDayOfWeek": "sunday",
                "index": "first",
            },
            "range": {
                "type": "noEnd",
                "startDate": "2020-07-05",
                "endDate": "0001-01-01",
                "recurrenceTimeZone": "UTC",
                "numberOfOccurrences": 0,
            },
        }

        recurrence = converter.obj_converter(data)

        assert isinstance(recurrence.pattern, patterns.YearlyAbsolute) is True
        assert isinstance(recurrence.range, ranges.NoEnd) is True

    def test_recurrence_converter_when_none(self):
        converter = RecurrenceConverter()
        assert converter.obj_converter(None) is None

    def test_recurrence_back_converter(self):
        converter = RecurrenceConverter()
        data = Recurrence(
            patterns.Daily(interval=1), ranges.NoEnd(start_date=date(2020, 5, 16))
        )
        assert converter.back_converter(data) == {
            "range": {"type": "noEnd"},
            "pattern": {"type": "daily", "interval": 1},
        }

    def test_recurrence_back_converter_when_none(self):
        converter = RecurrenceConverter()
        assert converter.back_converter(None) is None
