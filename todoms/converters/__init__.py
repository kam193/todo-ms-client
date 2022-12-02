from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar

T = TypeVar("T")


class BaseConverter(ABC, Generic[T]):
    @abstractmethod
    def obj_converter(self, data: Any) -> Optional[T]:
        pass

    @abstractmethod
    def back_converter(self, data: Optional[T]) -> Any:
        pass
