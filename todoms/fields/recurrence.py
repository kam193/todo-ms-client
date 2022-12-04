from datetime import date, datetime
from typing import Optional

from ..convertable import BaseConvertableFieldsObject
from ..converters.basic import DatetimeConverter
from ..converters.recurrence import RecurrenceConverter
from ..recurrence.ranges import BaseRecurrenceRange
from . import Field


class RecurrenceField(Field):
    _converter = RecurrenceConverter()


class DueDatetime(Field[datetime, dict]):
    _converter = DatetimeConverter()

    def _find_recurrence_start_date(
        self, instance: BaseConvertableFieldsObject
    ) -> Optional[datetime]:
        def _extract_datetime(range: BaseRecurrenceRange) -> Optional[datetime]:
            if not range.start_date:
                return None
            if isinstance(range.start_date, datetime):
                return range.start_date
            if isinstance(range.start_date, date):
                return datetime.combine(range.start_date, datetime.min.time())
            return None

        for field in instance._fields:
            if isinstance(field, RecurrenceField):
                recurrence = field._get_value(instance)
                if recurrence and recurrence.range:
                    return _extract_datetime(recurrence.range)

        return None

    def _get_value(self, instance: BaseConvertableFieldsObject) -> Optional[datetime]:
        value = super()._get_value(instance)
        if not value:
            return self._find_recurrence_start_date(instance)
        return value
