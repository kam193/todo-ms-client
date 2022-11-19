# TODO: Type hints

from abc import ABC
from typing import Type, Union

from . import BaseConverter
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


class Field(ABC):
    _converter = BaseConverter

    def __init__(self, dict_name: str):
        self.dict_name = dict_name

    def __set_name__(self, _, name):
        self.name = name

    def __get__(self, instance, _=None):
        if not instance:
            return self
        return self._get_value(instance)

    def __set__(self, instance, value):
        self._set_value(instance, value)

    def from_dict(self, instance, data: dict):
        if self.dict_name not in data:
            return
        self._set_value(instance, self.convert_from_dict(data))

    def to_dict(self, instance) -> dict:
        return {self.dict_name: self.convert_to_dict(instance)}

    def convert_from_dict(self, data: dict):
        if not data.get(self.dict_name):
            return None

        return self._converter.obj_converter(data[self.dict_name])

    def convert_to_dict(self, instance):
        if not self._get_value(instance):
            return None

        return self._converter.back_converter(self._get_value(instance))

    def _get_value(self, instance):
        return instance.__dict__.get(self.name)

    def _set_value(self, instance, value):
        instance.__dict__[self.name] = value


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
