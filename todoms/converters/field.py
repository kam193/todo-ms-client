# TODO: Type hints

from typing import Type, Union

from . import BaseConverter, Field
from .basic import (
    AttributeConverter,
    ContentAttrConverter,
    DateAttrConverter,
    DatetimeAttrConverter,
    ImportanceAttrConverter,
    IsoTimeAttrConverter,
    ListConverter,
    RecurrencePatternTypeAttrConverter,
    RecurrenceRangeTypeAttrConverter,
    StatusAttrConverter,
    WeekdayAttrConverter,
)


class Attribute(Field):
    _converter = AttributeConverter


class Datetime(Field):
    _converter = DatetimeAttrConverter


class Content(Field):
    _converter = ContentAttrConverter


class IsoTime(Field):
    _converter = IsoTimeAttrConverter


class Date(Field):
    _converter = DateAttrConverter


class List(Field):
    _converter = ListConverter

    def __init__(
        self, dict_name: str, inner_field: Union[Type[Field], Type[BaseConverter]]
    ):
        super().__init__(dict_name)
        if issubclass(inner_field, Field):
            self._converter = ListConverter(inner_field._converter)
        else:
            self._converter = ListConverter(inner_field)


class ImportanceField(Field):
    _converter = ImportanceAttrConverter


class StatusField(Field):
    _converter = StatusAttrConverter


class RecurrencePatternTypeField(Field):
    _converter = RecurrencePatternTypeAttrConverter


class RecurrenceRangeTypeField(Field):
    _converter = RecurrenceRangeTypeAttrConverter


class WeekdayField(Field):
    _converter = WeekdayAttrConverter
