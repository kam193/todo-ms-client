from abc import ABC
from typing import TYPE_CHECKING, Generic, Optional, TypeVar, Union

from ..converters import BaseConverter, JSONableTypes

if TYPE_CHECKING:
    from ..convertable import BaseConvertableFieldsObject, ConvertableType

# TODO: Type hinting

T = TypeVar("T")


class Field(ABC, Generic[T]):
    _converter: BaseConverter[T]

    def __init__(
        self,
        dict_name: str,
        default: Optional[T] = None,
        read_only: bool = False,
        export: bool = True,
    ) -> None:
        self.dict_name = dict_name
        self._default = default
        self._read_only = read_only
        self._export = export

    def _get_value(self, instance: ConvertableType) -> Optional[T]:
        return instance.__dict__.get(self.name, self._default)

    def __get__(
        self, instance: "BaseConvertableFieldsObject", _: object = None
    ) -> "Union[Optional[T], Field[T]]":
        if not instance:
            return self
        return self._get_value(instance)

    def _set_value(
        self, instance: "BaseConvertableFieldsObject", value: Optional[T]
    ) -> None:
        instance.__dict__[self.name] = value

    def __set__(
        self, instance: "BaseConvertableFieldsObject", value: Optional[T]
    ) -> None:
        if self._read_only:
            raise AttributeError("This field is read-only.")
        self._set_value(instance, value)

    def __delete__(self, instance: "BaseConvertableFieldsObject") -> None:
        if self.name in instance.__dict__:
            del instance.__dict__[self.name]

    def __set_name__(self, _: object, name: str) -> None:
        self.name = name

    def from_dict(self, instance: "BaseConvertableFieldsObject", data: dict) -> None:
        if self.dict_name not in data:
            return None
        self._set_value(instance, self.convert_from_dict(data))

    def to_dict(self, instance: "BaseConvertableFieldsObject") -> dict:
        if not self._export:
            return {}
        return {self.dict_name: self.convert_to_dict(instance)}

    def convert_from_dict(self, data: dict) -> Optional[T]:
        if data.get(self.dict_name) is None:
            return None

        return self._converter.obj_converter(data[self.dict_name])

    def convert_to_dict(self, instance: "BaseConvertableFieldsObject") -> JSONableTypes:
        if self._get_value(instance) is None:
            return None

        return self._converter.back_converter(self._get_value(instance))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} [{self.name}]>"
