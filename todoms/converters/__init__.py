from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar, Union

T = TypeVar("T")
JSONableTypes = Union[dict, list, str, int, bool, None]
# K = TypeVar("K", dict, list, str, int, bool, None)


class BaseConverter(ABC, Generic[T]):
    @abstractmethod
    def obj_converter(self, data: Any) -> Optional[T]:
        pass

    @abstractmethod
    def back_converter(self, data: Optional[T]) -> JSONableTypes:
        pass
