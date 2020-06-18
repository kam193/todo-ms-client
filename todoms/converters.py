from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from dateutil import parser, tz

from .attributes import Importance, Sensitivity, Status


@dataclass
class AttributeConverter:
    original_name: str
    local_name: str

    def obj_converter(self, data: Any) -> Any:
        return data

    def back_converter(self, data: Any) -> Any:
        return data


@dataclass
class DatetimeAttrConverter(AttributeConverter):
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


@dataclass
class ContentAttrConverter(AttributeConverter):
    def obj_converter(self, data: dict) -> str:
        if not data:
            return ""
        return data["content"]

    def back_converter(self, data: str) -> dict:
        return {"content": data, "contentType": "html"}


@dataclass
class IsoTimeAttrConverter(AttributeConverter):
    def obj_converter(self, data: str) -> datetime:
        return parser.isoparse(data)

    def back_converter(self, data: datetime) -> str:
        if not data:
            return None
        return data.astimezone(tz.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class EnumAttrConverter(AttributeConverter, ABC):
    _ENUM = None

    def obj_converter(self, data: str) -> Enum:
        if not data:
            return None
        return self._ENUM(data)

    def back_converter(self, data: Enum) -> str:
        if not data:
            return None
        return data.value


@dataclass
class ImportanceAttrConverter(EnumAttrConverter):
    _ENUM = Importance


@dataclass
class SensitivityAttrConverter(EnumAttrConverter):
    _ENUM = Sensitivity


@dataclass
class StatusAttrConverter(EnumAttrConverter):
    _ENUM = Status
