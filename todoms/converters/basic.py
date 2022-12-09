from abc import ABC
from datetime import date, datetime
from enum import Enum
from typing import Generic, List, Optional, Type, TypeVar

from dateutil import parser, tz

from todoms.attributes import Content, ContentType

from ..convertable import ConvertableType
from . import BaseConverter, JSONableTypes


class AttributeConverter(BaseConverter[JSONableTypes, JSONableTypes]):
    def obj_converter(self, data: Optional[JSONableTypes]) -> JSONableTypes:
        return data

    def back_converter(self, data: JSONableTypes) -> Optional[JSONableTypes]:
        return data


class BooleanConverter(BaseConverter[bool, bool]):
    def obj_converter(self, data: Optional[bool]) -> bool:
        return True if data else False

    def back_converter(self, data: Optional[bool]) -> Optional[bool]:
        return data


class DatetimeConverter(BaseConverter[datetime, dict]):
    def obj_converter(self, data: Optional[dict]) -> Optional[datetime]:
        if not data:
            return None

        date = parser.parse(data["dateTime"])
        return datetime.combine(date.date(), date.time(), tz.gettz(data["timeZone"]))

    def back_converter(self, data: Optional[datetime]) -> Optional[dict]:
        if not data:
            return None

        return {
            "dateTime": data.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "timeZone": data.tzname(),
        }


class ContentConverter(BaseConverter[Content, dict]):
    def obj_converter(self, data: Optional[dict]) -> Content:
        if not data:
            return Content(None, ContentType.HTML)
        return Content(data["content"], ContentType(data.get("contentType", "html")))

    def back_converter(self, data: Optional[Content]) -> Optional[dict]:
        value = data.value if data else None
        type_ = data.type if data else ContentType.HTML
        return {"content": value, "contentType": type_.value}


class IsoTimeConverter(BaseConverter[datetime, str]):
    def obj_converter(self, data: Optional[str]) -> Optional[datetime]:
        if not data:
            return None
        return parser.isoparse(data)

    def back_converter(self, data: Optional[datetime]) -> Optional[str]:
        if not data:
            return None
        return data.astimezone(tz.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


class DateConverter(BaseConverter[date, str]):
    def obj_converter(self, data: Optional[str]) -> Optional[date]:
        if not data:
            return None
        return parser.parse(data).date()

    def back_converter(self, data: Optional[date]) -> Optional[str]:
        if not data:
            return None
        return data.isoformat()


T = TypeVar("T")


class ListConverter(Generic[T], BaseConverter[List[T], list]):
    def __init__(self, obj_converter: BaseConverter[T, JSONableTypes]):
        self._converter = obj_converter

    def obj_converter(self, data: Optional[List[JSONableTypes]]) -> Optional[List[T]]:
        if data is None:
            return None
        return [
            self._converter.obj_converter(element)  # type: ignore
            for element in data
            if data  # The incompatible type None is filtered out here
        ]

    def back_converter(self, data: Optional[List[T]]) -> Optional[List[JSONableTypes]]:
        if data is None:
            return None
        return [self._converter.back_converter(element) for element in data]


TEnum = TypeVar("TEnum", bound=Enum)


class EnumConverter(BaseConverter[TEnum, str], ABC):
    _ENUM: Type[TEnum]

    def __init__(self, enum: Type[TEnum]):
        self._ENUM = enum

    def obj_converter(self, data: Optional[str]) -> Optional[TEnum]:
        if not data:
            return None
        return self._ENUM(data)

    def back_converter(self, data: Optional[TEnum]) -> Optional[str]:
        if not data:
            return None
        return str(data.value)


class ResourceConverter(BaseConverter[ConvertableType, dict]):
    _TYPE: Type[ConvertableType]

    def __init__(self, resource_class: Type[ConvertableType]) -> None:
        self._TYPE = resource_class
        super().__init__()

    def obj_converter(self, data: Optional[dict]) -> Optional[ConvertableType]:
        if not data:
            return None
        return self._TYPE.from_dict(data)

    def back_converter(self, data: Optional[ConvertableType]) -> Optional[dict]:
        if not data:
            return None
        return data.to_dict()
