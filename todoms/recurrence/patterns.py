from typing import Any

from todoms.converters.basic import EnumConverter

from ..attributes import RecurrencePatternType, Weekday
from ..convertable import BaseConvertableFieldsObject
from ..fields.basic import Attribute, EnumField, List


class BaseRecurrencePattern(BaseConvertableFieldsObject):
    interval = Attribute("interval")
    _pattern_type = EnumField("type", RecurrencePatternType)


class Daily(BaseRecurrencePattern):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(_pattern_type=RecurrencePatternType.DAILY, *args, **kwargs)


class Weekly(BaseRecurrencePattern):
    week_start = EnumField("firstDayOfWeek", Weekday)
    days_of_week = List("daysOfWeek", EnumConverter(Weekday))

    def __init__(self, *args: Any, week_start: Weekday = Weekday.SUNDAY, **kwargs: Any):
        super().__init__(
            _pattern_type=RecurrencePatternType.WEEKLY,
            *args,
            week_start=week_start,
            **kwargs
        )


class MonthlyAbsolute(BaseRecurrencePattern):
    day_of_month = Attribute("dayOfMonth")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(
            _pattern_type=RecurrencePatternType.MONTHLY_ABSOLUTE, *args, **kwargs
        )


class MonthlyRelative(BaseRecurrencePattern):
    days_of_week = List("daysOfWeek", EnumConverter(Weekday))

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(
            _pattern_type=RecurrencePatternType.MONTHLY_RELATIVE, *args, **kwargs
        )


class YearlyAbsolute(BaseRecurrencePattern):
    day_of_month = Attribute("dayOfMonth")
    month = Attribute("month")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(
            _pattern_type=RecurrencePatternType.YEARLY_ABSOLUTE, *args, **kwargs
        )


class YearlyRelative(BaseRecurrencePattern):
    days_of_week = List("daysOfWeek", EnumConverter(Weekday))
    month = Attribute("month")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(
            _pattern_type=RecurrencePatternType.YEARLY_RELATIVE, *args, **kwargs
        )
