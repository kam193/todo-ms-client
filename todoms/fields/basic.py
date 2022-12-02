# TODO: Type hints

from enum import Enum
from typing import Type, Union

from ..attributes import Content
from ..converters import BaseConverter
from ..converters.basic import (
    AttributeConverter,
    BooleanConverter,
    ContentConverter,
    DateConverter,
    DatetimeConverter,
    EnumConverter,
    IsoTimeConverter,
    ListConverter,
)
from . import Field


class Attribute(Field):
    _converter = AttributeConverter()


class Boolean(Field):
    _converter = BooleanConverter()


class Datetime(Field):
    _converter = DatetimeConverter()


class ContentField(Field):
    _converter = ContentConverter()

    def _set_value(self, instance, value):
        if isinstance(value, str):
            obj = self._get_value(instance) or Content(value)
            obj.value = value
            value = obj
        instance.__dict__[self.name] = value


class IsoTime(Field):
    _converter = IsoTimeConverter()


class Date(Field):
    _converter = DateConverter()


class List(Field):
    _converter = None

    def __init__(self, dict_name: str, inner_field: Union[Type[Field], BaseConverter]):
        super().__init__(dict_name)
        if isinstance(inner_field, BaseConverter):
            self._converter = ListConverter(inner_field)
        else:
            self._converter = ListConverter(inner_field._converter)


class EnumField(Field):
    _converter = None

    def __init__(self, dict_name: str, enum_class: Type[Enum], **kwargs):
        super().__init__(dict_name, **kwargs)
        self._converter = EnumConverter(enum_class)
