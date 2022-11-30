from abc import ABC
from datetime import date, datetime
from enum import Enum
from typing import Any, List, Type

from dateutil import parser, tz

from todoms.attributes import Content, ContentType

from . import BaseConverter


class AttributeConverter(BaseConverter):
    def obj_converter(self, data: Any) -> Any:
        return data

    def back_converter(self, data: Any) -> Any:
        return data


class DatetimeConverter(AttributeConverter):
    def obj_converter(self, data: dict) -> datetime:
        if not data:
            return None

        date = parser.parse(data["dateTime"])
        return datetime.combine(date.date(), date.time(), tz.gettz(data["timeZone"]))

    def back_converter(self, data: datetime) -> dict:
        if not data:
            return None

        return {
            "dateTime": data.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "timeZone": data.tzname(),
        }


class ContentConverter(AttributeConverter):
    def obj_converter(self, data: dict) -> str:
        if not data:
            return Content(None, ContentType.HTML)
        return Content(data["content"], ContentType(data.get("contentType", "html")))

    def back_converter(self, data: Content) -> dict:
        value = data.value if data else None
        type_ = data.type if data else ContentType.HTML
        return {"content": value, "contentType": type_.value}


class IsoTimeConverter(AttributeConverter):
    def obj_converter(self, data: str) -> datetime:
        return parser.isoparse(data)

    def back_converter(self, data: datetime) -> str:
        if not data:
            return None
        return data.astimezone(tz.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


class DateConverter(AttributeConverter):
    def obj_converter(self, data: str) -> date:
        return parser.parse(data).date()

    def back_converter(self, data: date) -> str:
        if not data:
            return None
        return data.isoformat()


class ListConverter(AttributeConverter):
    def __init__(self, obj_converter: AttributeConverter):
        self._converter = obj_converter

    def obj_converter(self, data: List[Any]) -> List[Any]:
        if data is None:
            return None
        return [self._converter.obj_converter(element) for element in data]

    def back_converter(self, data: List[Any]) -> List[Any]:
        if data is None:
            return None
        return [self._converter.back_converter(element) for element in data]

    @property
    def original_name(self) -> str:
        return self._converter.original_name

    @property
    def local_name(self) -> str:
        return self._converter.local_name


class EnumConverter(AttributeConverter, ABC):
    _ENUM = None

    def __init__(self, enum: Type[Enum]):
        self._ENUM = enum

    def obj_converter(self, data: str) -> Enum:
        if not data:
            return None
        return self._ENUM(data)

    def back_converter(self, data: Enum) -> str:
        if not data:
            return None
        return data.value
