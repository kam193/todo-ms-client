from ..attributes import RecurrencePatternType, Weekday
from ..convertable import BaseConvertableFieldsObject
from ..fields.basic import Attribute, List, RecurrencePatternTypeField, WeekdayField


class BaseRecurrencePattern(BaseConvertableFieldsObject):
    interval = Attribute("interval")
    _pattern_type = RecurrencePatternTypeField("type")


class Daily(BaseRecurrencePattern):
    def __init__(self, *args, **kwargs):
        super().__init__(_pattern_type=RecurrencePatternType.DAILY, *args, **kwargs)


class Weekly(BaseRecurrencePattern):
    week_start = WeekdayField("firstDayOfWeek")
    days_of_week = List("daysOfWeek", WeekdayField)

    def __init__(self, *args, week_start: Weekday = Weekday.SUNDAY, **kwargs):
        super().__init__(
            _pattern_type=RecurrencePatternType.WEEKLY,
            *args,
            week_start=week_start,
            **kwargs
        )


class MonthlyAbsolute(BaseRecurrencePattern):
    day_of_month = Attribute("dayOfMonth")

    def __init__(self, *args, **kwargs):
        super().__init__(
            _pattern_type=RecurrencePatternType.MONTHLY_ABSOLUTE, *args, **kwargs
        )


class MonthlyRelative(BaseRecurrencePattern):
    days_of_week = List("daysOfWeek", WeekdayField)

    def __init__(self, *args, **kwargs):
        super().__init__(
            _pattern_type=RecurrencePatternType.MONTHLY_RELATIVE, *args, **kwargs
        )


class YearlyAbsolute(BaseRecurrencePattern):
    day_of_month = Attribute("dayOfMonth")
    month = Attribute("month")

    def __init__(self, *args, **kwargs):
        super().__init__(
            _pattern_type=RecurrencePatternType.YEARLY_ABSOLUTE, *args, **kwargs
        )


class YearlyRelative(BaseRecurrencePattern):
    days_of_week = List("daysOfWeek", WeekdayField)
    month = Attribute("month")

    def __init__(self, *args, **kwargs):
        super().__init__(
            _pattern_type=RecurrencePatternType.YEARLY_RELATIVE, *args, **kwargs
        )
