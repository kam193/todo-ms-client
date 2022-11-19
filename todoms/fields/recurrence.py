from ..converters.recurrence import RecurrenceAttrConverter
from . import Field


class RecurrenceField(Field):
    _converter = RecurrenceAttrConverter
