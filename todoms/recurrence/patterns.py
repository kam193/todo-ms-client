from typing import Iterable

from ..attributes import RecurrencePatternType, Weekday
from ..convertable import BaseConvertableObject
from ..converters.basic import (
    AttributeConverter,
    ListConverter,
    RecurrencePatternTypeAttrConverter,
    WeekdayAttrConverter,
)


class BaseRecurrencePattern(BaseConvertableObject):
    ATTRIBUTES = (
        "interval",
        RecurrencePatternTypeAttrConverter("type", "_pattern_type"),
    )

    def __init__(self, pattern_type: RecurrencePatternType, interval: int):
        self._pattern_type = pattern_type
        self.interval = interval


class Daily(BaseRecurrencePattern):
    def __init__(self, interval: int):
        super().__init__(RecurrencePatternType.DAILY, interval)


class Weekly(BaseRecurrencePattern):
    ATTRIBUTES = (
        *BaseRecurrencePattern.ATTRIBUTES,
        WeekdayAttrConverter("firstDayOfWeek", "week_start"),
        ListConverter(WeekdayAttrConverter("daysOfWeek", "days_of_week")),
    )

    def __init__(
        self,
        interval: int,
        days_of_week: Iterable[Weekday],
        week_start: Weekday = Weekday.SUNDAY,
    ):
        super().__init__(RecurrencePatternType.WEEKLY, interval)
        self.days_of_week = days_of_week
        self.week_start = week_start


class MonthlyAbsolute(BaseRecurrencePattern):
    ATTRIBUTES = (
        *BaseRecurrencePattern.ATTRIBUTES,
        AttributeConverter("dayOfMonth", "day_of_month"),
    )

    def __init__(self, interval: int, day_of_month: int):
        super().__init__(RecurrencePatternType.MONTHLY_ABSOLUTE, interval)
        self.day_of_month = day_of_month


class MonthlyRelative(BaseRecurrencePattern):
    ATTRIBUTES = (
        *BaseRecurrencePattern.ATTRIBUTES,
        ListConverter(WeekdayAttrConverter("daysOfWeek", "days_of_week")),
    )

    def __init__(self, interval: int, days_of_week: Iterable[Weekday]):
        super().__init__(RecurrencePatternType.MONTHLY_RELATIVE, interval)
        self.days_of_week = days_of_week


class YearlyAbsolute(BaseRecurrencePattern):
    ATTRIBUTES = (
        *BaseRecurrencePattern.ATTRIBUTES,
        AttributeConverter("dayOfMonth", "day_of_month"),
        "month",
    )

    def __init__(self, interval: int, day_of_month: int, month: int):
        super().__init__(RecurrencePatternType.YEARLY_ABSOLUTE, interval)
        self.day_of_month = day_of_month
        self.month = month


class YearlyRelative(BaseRecurrencePattern):
    ATTRIBUTES = (
        *BaseRecurrencePattern.ATTRIBUTES,
        ListConverter(WeekdayAttrConverter("daysOfWeek", "days_of_week")),
        "month",
    )

    def __init__(self, interval: int, days_of_week: Iterable[Weekday], month: int):
        super().__init__(RecurrencePatternType.YEARLY_RELATIVE, interval)
        self.days_of_week = days_of_week
        self.month = month
