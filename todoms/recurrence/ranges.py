from datetime import datetime

from ..attributes import RecurrenceRangeType
from ..convertable import BaseConvertableObject
from ..converters.basic import (
    AttributeConverter,
    DateAttrConverter,
    RecurrenceRangeTypeAttrConverter,
)


class BaseRecurrenceRange(BaseConvertableObject):
    ATTRIBUTES = (
        RecurrenceRangeTypeAttrConverter("type", "_range_type"),
        DateAttrConverter("startDate", "start_date"),
    )

    def __init__(self, range_type: RecurrenceRangeType, start_date: datetime):
        self._range_type = range_type
        self.start_date = start_date


class EndDate(BaseRecurrenceRange):
    ATTRIBUTES = (
        *BaseRecurrenceRange.ATTRIBUTES,
        DateAttrConverter("endDate", "end_date"),
    )

    def __init__(self, start_date: datetime, end_date: datetime):
        super().__init__(RecurrenceRangeType.END_DATE, start_date)
        self.end_date = end_date


class NoEnd(BaseRecurrenceRange):
    def __init__(self, start_date: datetime):
        super().__init__(RecurrenceRangeType.NO_END, start_date)


class Numbered(BaseRecurrenceRange):
    ATTRIBUTES = (
        *BaseRecurrenceRange.ATTRIBUTES,
        AttributeConverter("numberOfOccurrences", "occurrences"),
    )

    def __init__(self, start_date: datetime, occurrences: int):
        super().__init__(RecurrenceRangeType.NUMBERED, start_date)
        self.occurrences = occurrences
