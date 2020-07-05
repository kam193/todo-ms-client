from todoms.converters.recurrence import (
    RecurrencePatternAttrConverter,
    RecurrenceRangeAttrConverter,
)
from todoms.recurrence import patterns, ranges
import pytest
from datetime import datetime
from dateutil import tz


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
        converter = RecurrencePatternAttrConverter("", "")
        assert isinstance(converter.obj_converter(data), expected_class) is True

    def test_recurrence_patterns_converter_when_invalid(self):
        converter = RecurrencePatternAttrConverter("", "")
        with pytest.raises(ValueError):
            converter.obj_converter({"type": "some invalid"})

    def test_recurrence_patterns_converter_when_none(self):
        converter = RecurrencePatternAttrConverter("", "")
        assert converter.obj_converter(None) is None

    def test_recurrence_pattern_back_converter(self):
        converter = RecurrencePatternAttrConverter("", "")
        data = patterns.Daily(3)

        assert converter.back_converter(data) == {"type": "daily", "interval": 3}

    def test_recurrence_pattern_back_converter_when_none(self):
        converter = RecurrencePatternAttrConverter("", "")
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
        converter = RecurrenceRangeAttrConverter("", "")
        assert isinstance(converter.obj_converter(data), expected_class) is True

    def test_recurrence_range_converter_when_invalid(self):
        converter = RecurrenceRangeAttrConverter("", "")
        with pytest.raises(ValueError):
            converter.obj_converter({"type": "invalid"})

    def test_recurrence_range_converter_when_none(self):
        converter = RecurrenceRangeAttrConverter("", "")
        assert converter.obj_converter(None) is None

    def test_recurrence_range_back_converter(self):
        converter = RecurrenceRangeAttrConverter("", "")
        data = ranges.EndDate(
            start_date=datetime(2020, 4, 8, 16, tzinfo=tz.UTC),
            end_date=datetime(2022, 4, 8, 16, tzinfo=tz.UTC),
        )
        assert converter.back_converter(data) == {
            "type": "endDate",
            "startDate": "2020-04-08T16:00:00Z",
            "endDate": "2022-04-08T16:00:00Z",
        }

    def test_recurrence_range_back_converter_when_none(self):
        converter = RecurrenceRangeAttrConverter("", "")
        assert converter.back_converter(None) is None
