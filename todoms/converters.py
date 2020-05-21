from typing import Callable, Any
from dataclasses import dataclass

from datetime import datetime
from dateutil import parser
from dateutil.tz import gettz


@dataclass
class AttributeConverter:
    original_name: str
    local_name: str
    obj_converter: Callable[[Any], Any] = lambda x: x


def datetime_dict_converter(data: dict) -> datetime:
    date = parser.parse(data["dateTime"])
    return datetime.combine(date.date(), date.time(), gettz(data["timeZone"]))
