from ..converters.recurrence import RecurrenceConverter
from . import Field


class RecurrenceField(Field):
    _converter = RecurrenceConverter()
