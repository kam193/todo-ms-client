from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar, Union

T = TypeVar("T")
JSONableTypes = Union[dict, list, str, int, bool, None]
KSourceType = TypeVar(
    "KSourceType", dict, list, str, int, bool, None, JSONableTypes, covariant=True
)


class BaseConverter(ABC, Generic[T, KSourceType]):
    @abstractmethod
    def obj_converter(self, data: Optional[KSourceType]) -> Optional[T]:
        pass

    @abstractmethod
    def back_converter(self, data: Optional[T]) -> Optional[KSourceType]:
        pass
