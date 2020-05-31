from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

from dateutil import parser
from dateutil.tz import gettz


@dataclass
class AttributeConverter:
    original_name: str
    local_name: str

    def obj_converter(self, data: Any) -> Any:
        return data


@dataclass
class DatetimeAttrConverter(AttributeConverter):
    def obj_converter(self, data: dict) -> datetime:
        if not data:
            return None

        date = parser.parse(data["dateTime"])
        return datetime.combine(date.date(), date.time(), gettz(data["timeZone"]))


@dataclass
class ContentAttrConverter(AttributeConverter):
    def obj_converter(self, data: dict) -> str:
        if not data:
            return ""
        return data["content"]


@dataclass
class IsoTimeAttrConverter(AttributeConverter):
    def obj_converter(self, data: str) -> datetime:
        return parser.isoparse(data)
