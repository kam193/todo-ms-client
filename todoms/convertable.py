import inspect
from abc import ABC

from .fields import Field


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

    def __init__(self, **kwargs):
        for field in self._fields:
            if field.name in kwargs:
                setattr(self, field.name, kwargs[field.name])

    @classmethod
    def from_dict(
        cls, data: dict, **additional_kwargs
    ) -> "BaseConvertableFieldsObject":
        instance = cls(**additional_kwargs)
        for field in instance._fields:
            field.from_dict(instance, data)
        return instance

    def to_dict(self) -> dict:
        data = {}
        for field in self._fields:
            data.update(field.to_dict(self))
        return data

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__})"
