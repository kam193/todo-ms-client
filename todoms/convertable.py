from abc import ABC

from .converters import BaseConverter


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
    def create_from_dict(cls, data_dict: dict, **additional_kwargs):
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
