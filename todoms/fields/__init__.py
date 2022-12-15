from abc import ABC
from typing import TYPE_CHECKING, Callable, Generic, Optional, TypeVar, Union

from ..converters import BaseConverter, KSourceType

if TYPE_CHECKING:
    from ..convertable import BaseConvertableFieldsObject, ConvertableType


T = TypeVar("T")


class Field(ABC, Generic[T, KSourceType]):
    _converter: BaseConverter[T, KSourceType]

    def __init__(
        self,
        dict_name: str,
        default: Optional[T] = None,
        default_factory: Optional[Callable[[], Optional[T]]] = None,
        read_only: bool = False,
        export: bool = True,
        post_convert: Optional[Callable[["ConvertableType", T], T]] = None,
    ) -> None:
        self.dict_name = dict_name
        self._read_only = read_only
        self._export = export
        self._post_convert = post_convert

        self._default_factory: Callable[[], Optional[T]]
        if not default_factory:
            self._default_factory = lambda: default
        else:
            self._default_factory = default_factory

    def _set_value(
        self, instance: "BaseConvertableFieldsObject", value: Optional[T]
    ) -> None:
        instance.__dict__[self.name] = value

    def _get_value(self, instance: "ConvertableType") -> Optional[T]:
        if self.name not in instance.__dict__:
            self._set_value(instance, self._default_factory())
        return instance.__dict__.get(self.name)

    def __get__(
        self, instance: "BaseConvertableFieldsObject", _: object = None
    ) -> "Union[Optional[T], Field[T, KSourceType]]":
        if not instance:
            return self
        return self._get_value(instance)

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

    def from_dict(self, instance: "ConvertableType", data: dict) -> None:
        if self.dict_name not in data:
            return None
        value = self.convert_from_dict(data)
        if value and self._post_convert:
            value = self._post_convert(instance, value)
        self._set_value(instance, value)

    def to_dict(self, instance: "BaseConvertableFieldsObject") -> dict:
        if not self._export:
            return {}
        return {self.dict_name: self.convert_to_dict(instance)}

    def convert_from_dict(self, data: dict) -> Optional[T]:
        if data.get(self.dict_name) is None:
            return None

        return self._converter.obj_converter(data[self.dict_name])

    def convert_to_dict(
        self, instance: "BaseConvertableFieldsObject"
    ) -> Optional[KSourceType]:
        if self._get_value(instance) is None:
            return None

        return self._converter.back_converter(self._get_value(instance))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} [{self.name}]>"
