# TODO: Type hints

from enum import Enum
from typing import Type, Union

from ..converters import BaseConverter
from ..converters.basic import (
    AttributeConverter,
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


class Datetime(Field):
    _converter = DatetimeConverter()


class Content(Field):
    _converter = ContentConverter()


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

    def __init__(self, dict_name: str, enum_class: Type[Enum]):
        super().__init__(dict_name)
        self._converter = EnumConverter(enum_class)
