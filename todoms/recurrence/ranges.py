from todoms.fields.basic import Attribute, Date, EnumField

from ..attributes import RecurrenceRangeType
from ..convertable import BaseConvertableFieldsObject


class BaseRecurrenceRange(BaseConvertableFieldsObject):
    _range_type = EnumField("type", RecurrenceRangeType)
    start_date = Date("startDate")


class EndDate(BaseRecurrenceRange):
    end_date = Date("endDate")

    def __init__(self, *args, **kwargs):
        super().__init__(_range_type=RecurrenceRangeType.END_DATE, *args, **kwargs)


class NoEnd(BaseRecurrenceRange):
    def __init__(self, *args, **kwargs):
        super().__init__(_range_type=RecurrenceRangeType.NO_END, *args, **kwargs)


class Numbered(BaseRecurrenceRange):
    occurrences = Attribute("numberOfOccurrences")

    def __init__(self, *args, **kwargs):
        super().__init__(_range_type=RecurrenceRangeType.NUMBERED, *args, **kwargs)
