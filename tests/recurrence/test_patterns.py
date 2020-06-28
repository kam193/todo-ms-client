from todoms.attributes import RecurrencePatternType
from todoms.recurrence.patterns import (
    BaseRecurrencePattern,
    Daily,
    MonthlyAbsolute,
    MonthlyRelative,
    Weekday,
    Weekly,
    YearlyAbsolute,
    YearlyRelative,
)


def test_base_pattern_to_dict():
    pattern = BaseRecurrencePattern(RecurrencePatternType.WEEKLY, 101)

    assert pattern.to_dict() == {"type": "weekly", "interval": 101}


def test_daily_recurrence_pattern_to_dict():
    pattern = Daily(3)

    assert pattern.to_dict() == {"type": "daily", "interval": 3}


def test_weekly_recurrence_pattern_to_dict():
    pattern = Weekly(interval=6, days_of_week=[Weekday.MONDAY, Weekday.FRIDAY])

    assert pattern.to_dict() == {
        "type": "weekly",
        "interval": 6,
        "daysOfWeek": ["monday", "friday"],
        "firstDayOfWeek": "sunday",
    }


def test_weekly_recurrence_pattern_with_first_day_to_dict():
    pattern = Weekly(
        interval=6,
        days_of_week=[Weekday.MONDAY, Weekday.FRIDAY],
        week_start=Weekday.WEDNESDAY,
    )

    assert pattern.to_dict() == {
        "type": "weekly",
        "interval": 6,
        "daysOfWeek": ["monday", "friday"],
        "firstDayOfWeek": "wednesday",
    }


def test_monthly_absolute_recurrence_pattern_to_dict():
    pattern = MonthlyAbsolute(interval=3, day_of_month=15)

    assert pattern.to_dict() == {
        "type": "absoluteMonthly",
        "interval": 3,
        "dayOfMonth": 15,
    }


def test_monthly_relative_recurrence_pattern_to_dict():
    pattern = MonthlyRelative(
        interval=3, days_of_week=[Weekday.FRIDAY, Weekday.SATURDAY]
    )

    assert pattern.to_dict() == {
        "type": "relativeMonthly",
        "interval": 3,
        "daysOfWeek": ["friday", "saturday"],
    }


def test_yearly_absolute_recurrence_pattern_to_dict():
    pattern = YearlyAbsolute(interval=1, day_of_month=17, month=6)

    assert pattern.to_dict() == {
        "type": "absoluteYearly",
        "interval": 1,
        "dayOfMonth": 17,
        "month": 6,
    }


def test_yearly_relative_recurrence_pattern_to_dict():
    pattern = YearlyRelative(
        interval=2, days_of_week=[Weekday.MONDAY, Weekday.THURSDAY], month=3
    )

    assert pattern.to_dict() == {
        "type": "relativeYearly",
        "interval": 2,
        "daysOfWeek": ["monday", "thursday"],
        "month": 3,
    }
