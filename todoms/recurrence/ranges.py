from typing import Any

from todoms.fields.basic import Attribute, Date, EnumField

from ..attributes import RecurrenceRangeType
from ..convertable import BaseConvertableFieldsObject


class BaseRecurrenceRange(BaseConvertableFieldsObject):
    _range_type = EnumField("type", RecurrenceRangeType)
    start_date = Date("startDate", export=False)


# TODO: Remove?
class EndDate(BaseRecurrenceRange):
    """This range is most probably not supported by the API"""

    end_date = Date("endDate", export=False)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(_range_type=RecurrenceRangeType.END_DATE, *args, **kwargs)


class NoEnd(BaseRecurrenceRange):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(_range_type=RecurrenceRangeType.NO_END, *args, **kwargs)


class Numbered(BaseRecurrenceRange):
    occurrences = Attribute("numberOfOccurrences")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(_range_type=RecurrenceRangeType.NUMBERED, *args, **kwargs)
