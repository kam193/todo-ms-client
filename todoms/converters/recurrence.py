from typing import Optional

from ..attributes import RecurrencePatternType, RecurrenceRangeType
from ..recurrence import Recurrence, patterns, ranges
from . import BaseConverter


class RecurrencePatternConverter(BaseConverter[patterns.BaseRecurrencePattern, dict]):
    _CONVERTING_TABLE: dict[str, type[patterns.BaseRecurrencePattern]] = {
        RecurrencePatternType.DAILY.value: patterns.Daily,
        RecurrencePatternType.WEEKLY.value: patterns.Weekly,
        RecurrencePatternType.MONTHLY_ABSOLUTE.value: patterns.MonthlyAbsolute,
        RecurrencePatternType.MONTHLY_RELATIVE.value: patterns.MonthlyRelative,
        RecurrencePatternType.YEARLY_ABSOLUTE.value: patterns.YearlyAbsolute,
        RecurrencePatternType.YEARLY_RELATIVE.value: patterns.YearlyRelative,
    }

    def obj_converter(self, data: Optional[dict]) -> patterns.BaseRecurrencePattern:
        if not data:
            raise ValueError("Recurrence pattern is required")

        pattern_class = self._CONVERTING_TABLE.get(
            data.get("type", RecurrencePatternType.DAILY.value)
        )
        if not pattern_class:
            raise ValueError

        return pattern_class.from_dict(data)

    def back_converter(
        self, data: Optional[patterns.BaseRecurrencePattern]
    ) -> Optional[dict]:
        if not data:
            return None
        return data.to_dict()


class RecurrenceRangeConverter(BaseConverter[ranges.BaseRecurrenceRange, dict]):
    _CONVERTING_TABLE: dict[str, type[ranges.BaseRecurrenceRange]] = {
        RecurrenceRangeType.END_DATE.value: ranges.EndDate,
        RecurrenceRangeType.NO_END.value: ranges.NoEnd,
        RecurrenceRangeType.NUMBERED.value: ranges.Numbered,
    }

    def obj_converter(self, data: Optional[dict]) -> ranges.BaseRecurrenceRange:
        if not data:
            raise ValueError("Recurrence range is required")

        pattern_class = self._CONVERTING_TABLE.get(
            data.get("type", RecurrenceRangeType.NO_END.value)
        )
        if not pattern_class:
            raise ValueError

        return pattern_class.from_dict(data)

    def back_converter(
        self, data: Optional[ranges.BaseRecurrenceRange]
    ) -> Optional[dict]:
        if not data:
            return None
        return data.to_dict()


class RecurrenceConverter(BaseConverter[Recurrence, dict]):
    _range_converter = RecurrenceRangeConverter()
    _pattern_converter = RecurrencePatternConverter()

    def obj_converter(self, data: Optional[dict]) -> Optional[Recurrence]:
        if not data:
            return None

        return Recurrence(
            self._pattern_converter.obj_converter(data.get("pattern")),
            self._range_converter.obj_converter(data.get("range")),
        )

    def back_converter(self, data: Optional[Recurrence]) -> Optional[dict]:
        if not data:
            return None

        return data.to_dict()
