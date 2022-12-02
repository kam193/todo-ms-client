from abc import ABC
from datetime import date, datetime
from enum import Enum
from typing import Any, List, Optional, Type, TypeVar

from dateutil import parser, tz

from todoms.attributes import Content, ContentType

from . import BaseConverter


class AttributeConverter(BaseConverter[Any]):
    def obj_converter(self, data: Any) -> Any:
        return data

    def back_converter(self, data: Any) -> Any:
        return data


class BooleanConverter(BaseConverter[bool]):
    def obj_converter(self, data: bool) -> bool:
        return True if data else False

    def back_converter(self, data: Optional[bool]) -> Optional[bool]:
        return data


class DatetimeConverter(BaseConverter[datetime]):
    def obj_converter(self, data: dict) -> Optional[datetime]:
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


class ContentConverter(BaseConverter[Content]):
    def obj_converter(self, data: dict) -> Content:
        if not data:
            return Content(None, ContentType.HTML)
        return Content(data["content"], ContentType(data.get("contentType", "html")))

    def back_converter(self, data: Optional[Content]) -> dict:
        value = data.value if data else None
        type_ = data.type if data else ContentType.HTML
        return {"content": value, "contentType": type_.value}


class IsoTimeConverter(BaseConverter[datetime]):
    def obj_converter(self, data: str) -> datetime:
        return parser.isoparse(data)

    def back_converter(self, data: Optional[datetime]) -> Optional[str]:
        if not data:
            return None
        return data.astimezone(tz.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


class DateConverter(BaseConverter[date]):
    def obj_converter(self, data: str) -> date:
        return parser.parse(data).date()

    def back_converter(self, data: Optional[date]) -> Optional[str]:
        if not data:
            return None
        return data.isoformat()


class ListConverter(BaseConverter[List[Any]]):
    def __init__(self, obj_converter: BaseConverter):
        self._converter = obj_converter

    # TODO: Generic type
    def obj_converter(self, data: Optional[List[Any]]) -> Optional[List[Any]]:
        if data is None:
            return None
        return [self._converter.obj_converter(element) for element in data]

    def back_converter(self, data: Optional[List[Any]]) -> Optional[List[Any]]:
        if data is None:
            return None
        return [self._converter.back_converter(element) for element in data]


TEnum = TypeVar("TEnum", bound=Enum)


class EnumConverter(BaseConverter[TEnum], ABC):
    _ENUM: Type[TEnum]

    def __init__(self, enum: Type[TEnum]):
        self._ENUM = enum

    def obj_converter(self, data: str) -> Optional[TEnum]:
        if not data:
            return None
        return self._ENUM(data)

    def back_converter(self, data: Optional[TEnum]) -> Optional[str]:
        if not data:
            return None
        return str(data.value)
