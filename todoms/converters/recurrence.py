from ..attributes import RecurrencePatternType, RecurrenceRangeType
from ..recurrence import Recurrence, patterns, ranges
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

    def obj_converter(self, data: dict) -> patterns.BaseRecurrencePattern:
        if not data:
            return None

        pattern_class = self._CONVERTING_TABLE.get(data.get("type"))
        if not pattern_class:
            raise ValueError

        return pattern_class.create_from_dict(data)

    def back_converter(self, data: patterns.BaseRecurrencePattern) -> dict:
        if not data:
            return None
        return data.to_dict()


class RecurrenceRangeAttrConverter(AttributeConverter):
    _CONVERTING_TABLE = {
        RecurrenceRangeType.END_DATE.value: ranges.EndDate,
        RecurrenceRangeType.NO_END.value: ranges.NoEnd,
        RecurrenceRangeType.NUMBERED.value: ranges.Numbered,
    }

    def obj_converter(self, data: dict) -> ranges.BaseRecurrenceRange:
        if not data:
            return None

        pattern_class = self._CONVERTING_TABLE.get(data.get("type"))
        if not pattern_class:
            raise ValueError

        return pattern_class.create_from_dict(data)

    def back_converter(self, data: ranges.BaseRecurrenceRange) -> dict:
        if not data:
            return None
        return data.to_dict()


class RecurrenceAttrConverter(AttributeConverter):
    _range_converter = RecurrenceRangeAttrConverter("", "")
    _pattern_converter = RecurrencePatternAttrConverter("", "")

    def obj_converter(self, data: dict) -> Recurrence:
        if not data:
            return None

        return Recurrence(
            self._pattern_converter.obj_converter(data.get("pattern")),
            self._range_converter.obj_converter(data.get("range")),
        )

    def back_converter(self, data: Recurrence) -> dict:
        if not data:
            return None

        return data.to_dict()
