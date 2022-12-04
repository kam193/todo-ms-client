import inspect
from abc import ABC
from typing import Any, Type, TypeVar

from .fields import Field

ConvertableType = TypeVar("ConvertableType", bound="BaseConvertableFieldsObject")


class BaseConvertableFieldsObject(ABC):
    """Base class for all resources. Supports conversion to and from dicts."""

    @property
    def _fields(self) -> list[Field]:
        return [
            v
            for _, v in inspect.getmembers(
                self.__class__, lambda m: issubclass(type(m), Field)
            )
        ]

    def __init__(self, **kwargs: Any) -> None:
        for field in self._fields:
            if field.name in kwargs:
                setattr(self, field.name, kwargs[field.name])

    @classmethod
    def from_dict(
        cls: Type[ConvertableType], data: dict, **additional_kwargs: Any
    ) -> ConvertableType:
        instance = cls(**additional_kwargs)
        instance._from_dict(data)
        return instance

    def _from_dict(self, data: dict) -> None:
        for field in self._fields:
            field.from_dict(self, data)

    def to_dict(self) -> dict:
        data = {}
        for field in self._fields:
            data.update(field.to_dict(self))
        return data

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__dict__})"
