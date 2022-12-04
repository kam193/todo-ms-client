from datetime import date, datetime
from enum import Enum
from typing import Any, Generic, Type, TypeVar, Union

from ..attributes import Content
from ..convertable import BaseConvertableFieldsObject
from ..converters import BaseConverter, JSONableTypes
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


class Attribute(Field[JSONableTypes, JSONableTypes]):
    _converter = AttributeConverter()


class Boolean(Field[bool, bool]):
    _converter = BooleanConverter()


class Datetime(Field[datetime, dict]):
    _converter = DatetimeConverter()


class ContentField(Field[Content, dict]):
    _converter = ContentConverter()

    def _set_value(
        self, instance: BaseConvertableFieldsObject, value: Union[Content, str, None]
    ) -> None:
        if isinstance(value, str):
            obj = self._get_value(instance) or Content(value)
            obj.value = value
            value = obj
        instance.__dict__[self.name] = value


class IsoTime(Field[datetime, str]):
    _converter = IsoTimeConverter()


class Date(Field[date, str]):
    _converter = DateConverter()


T = TypeVar("T")


class List(Generic[T], Field[list[T], list]):
    # _converter: ListConverter[T]

    def __init__(
        self,
        dict_name: str,
        inner_field: Union[
            Type[Field[T, JSONableTypes]], BaseConverter[T, JSONableTypes]
        ],
    ) -> None:
        super().__init__(dict_name)
        if isinstance(inner_field, BaseConverter):
            self._converter = ListConverter[T](inner_field)
        else:
            self._converter = ListConverter[T](inner_field._converter)


class EnumField(Field[Enum, str]):
    def __init__(self, dict_name: str, enum_class: Type[Enum], **kwargs: Any) -> None:
        super().__init__(dict_name, **kwargs)
        self._converter = EnumConverter(enum_class)
