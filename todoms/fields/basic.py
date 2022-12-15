from datetime import date, datetime
from enum import Enum
from typing import Any, Callable, Generic, Optional, Type, TypeVar, Union

from ..attributes import Content
from ..convertable import BaseConvertableFieldsObject, ConvertableType
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
        default: Optional[list[T]] = None,
        default_factory: Optional[Callable[[], Optional[list[T]]]] = None,
        read_only: bool = False,
        export: bool = True,
        post_convert: Optional[Callable[[ConvertableType, list[T]], list[T]]] = None,
    ) -> None:
        super().__init__(
            dict_name, default, default_factory, read_only, export, post_convert
        )
        if isinstance(inner_field, BaseConverter):
            self._converter = ListConverter[T](inner_field)
        else:
            self._converter = ListConverter[T](inner_field._converter)


TEnum = TypeVar("TEnum", bound=Enum)


class EnumField(Field[TEnum, str]):
    def __init__(self, dict_name: str, enum_class: Type[TEnum], **kwargs: Any) -> None:
        super().__init__(dict_name, **kwargs)
        self._converter = EnumConverter(enum_class)
