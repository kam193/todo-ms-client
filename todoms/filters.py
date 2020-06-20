from datetime import datetime
from enum import Enum
from itertools import chain
from typing import Dict, List, Union

from dateutil import tz

Comparable = Union[str, Enum, datetime, bool]


def _format_kwargs(kwargs: Dict) -> List[str]:
    return [f"{k} {v}" for k, v in kwargs.items()]


def _format_comparable(value: Comparable) -> str:
    if isinstance(value, Enum):
        return f"'{value.value}'"
    elif isinstance(value, datetime):
        return value.astimezone(tz.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    elif value is True:
        return "true"
    elif value is False:
        return "false"
    else:
        return f"'{value}'"


def _generate_operator(op, args, kwargs) -> str:
    if len(args) + len(kwargs) == 1:
        return "".join(chain(args, _format_kwargs(kwargs)))
    condition = f" {op} ".join(chain(args, _format_kwargs(kwargs)))
    return f"({condition.strip()})"


def and_(*args, **kwargs) -> str:
    return _generate_operator("and", args, kwargs)


def or_(*args, **kwargs) -> str:
    return _generate_operator("or", args, kwargs)


def eq(value: Comparable) -> str:
    return f"eq {_format_comparable(value)}"


def ne(value: Comparable) -> str:
    return f"ne {_format_comparable(value)}"


def gt(value: Comparable) -> str:
    return f"gt {_format_comparable(value)}"


def ge(value: Comparable) -> str:
    return f"ge {_format_comparable(value)}"


def lt(value: Comparable) -> str:
    return f"lt {_format_comparable(value)}"


def le(value: Comparable) -> str:
    return f"le {_format_comparable(value)}"
