from ..attributes import RecurrencePatternType, RecurrenceRangeType
from ..recurrence import Recurrence, patterns, ranges
from . import Field
from .basic import AttributeConverter


class RecurrencePatternAttrConverter(AttributeConverter):
    _CONVERTING_TABLE = {
        RecurrencePatternType.DAILY.value: patterns.Daily,
        RecurrencePatternType.WEEKLY.value: patterns.Weekly,
        RecurrencePatternType.MONTHLY_ABSOLUTE.value: patterns.MonthlyAbsolute,
        RecurrencePatternType.MONTHLY_RELATIVE.value: patterns.MonthlyRelative,
        RecurrencePatternType.YEARLY_ABSOLUTE.value: patterns.YearlyAbsolute,
        RecurrencePatternType.YEARLY_RELATIVE.value: patterns.YearlyRelative,
    }

    @classmethod
    def obj_converter(cls, data: dict) -> patterns.BaseRecurrencePattern:
        if not data:
            return None

        pattern_class = cls._CONVERTING_TABLE.get(data.get("type"))
        if not pattern_class:
            raise ValueError

        return pattern_class.from_dict(data)

    @classmethod
    def back_converter(cls, data: patterns.BaseRecurrencePattern) -> dict:
        if not data:
            return None
        return data.to_dict()


class RecurrenceRangeAttrConverter(AttributeConverter):
    # TODO: #104 - Support the way the recurrence is updated in the API
    # until then, updating the recurrence will not work
    _CONVERTING_TABLE = {
        RecurrenceRangeType.END_DATE.value: ranges.EndDate,
        RecurrenceRangeType.NO_END.value: ranges.NoEnd,
        RecurrenceRangeType.NUMBERED.value: ranges.Numbered,
    }

    @classmethod
    def obj_converter(cls, data: dict) -> ranges.BaseRecurrenceRange:
        if not data:
            return None

        pattern_class = cls._CONVERTING_TABLE.get(data.get("type"))
        if not pattern_class:
            raise ValueError

        return pattern_class.from_dict(data)

    @classmethod
    def back_converter(cls, data: ranges.BaseRecurrenceRange) -> dict:
        if not data:
            return None
        return data.to_dict()


class RecurrenceAttrConverter(AttributeConverter):
    _range_converter = RecurrenceRangeAttrConverter("", "")
    _pattern_converter = RecurrencePatternAttrConverter("", "")

    @classmethod
    def obj_converter(cls, data: dict) -> Recurrence:
        if not data:
            return None

        return Recurrence(
            cls._pattern_converter.obj_converter(data.get("pattern")),
            cls._range_converter.obj_converter(data.get("range")),
        )

    @classmethod
    def back_converter(cls, data: Recurrence) -> dict:
        if not data:
            return None

        return data.to_dict()


class RecurrenceField(Field):
    _converter = RecurrenceAttrConverter
