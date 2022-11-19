from abc import ABC

from .converters import BaseConverter
from .converters.field import Field


class BaseConvertableObject(ABC):
    ATTRIBUTES = ()

    def to_dict(self):
        """Convert resource into dict accepted by API"""
        data_dict = {}

        for attr in self.ATTRIBUTES:
            if isinstance(attr, BaseConverter):
                value = getattr(self, attr.local_name, None)
                data_dict[attr.original_name] = attr.back_converter(value)
            else:
                data_dict[attr] = getattr(self, attr, None)

        return data_dict

    @classmethod
    def from_dict(cls, data_dict: dict, **additional_kwargs):
        init_arguments = {}
        private_attributes = {}

        def store_attribute(name, value):
            if name.startswith("_"):
                private_attributes[name] = value
            else:
                init_arguments[name] = value

        for attr in cls.ATTRIBUTES:
            if isinstance(attr, BaseConverter):
                if attr.original_name in data_dict:
                    value = attr.obj_converter(data_dict.get(attr.original_name))
                    store_attribute(attr.local_name, value)
            elif attr in data_dict:
                store_attribute(attr, data_dict.get(attr))

        obj = cls(**init_arguments, **additional_kwargs)
        for attr, value in private_attributes.items():
            setattr(obj, attr, value)

        return obj


class BaseConvertableFieldsObject(BaseConvertableObject, ABC):
    """Base class for all resources. Supports conversion to and from dicts."""

    def __init__(self, **kwargs):
        for field in self._fields:
            if field.name in kwargs:
                setattr(self, field.name, kwargs[field.name])

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__})"

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

    @property
    def _fields(self) -> list[Field]:
        return [
            field
            for field in self.__class__.__dict__.values()
            if isinstance(field, Field)
        ]
