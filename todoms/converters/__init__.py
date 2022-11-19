from abc import ABC, abstractmethod
from typing import Any


class BaseConverter(ABC):
    @classmethod
    @abstractmethod
    def obj_converter(cls, data: Any) -> Any:
        pass

    @classmethod
    @abstractmethod
    def back_converter(cls, data: Any) -> Any:
        pass
