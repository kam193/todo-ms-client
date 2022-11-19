from abc import ABC, abstractmethod
from typing import Any


class BaseConverter(ABC):
    @abstractmethod
    def obj_converter(self, data: Any) -> Any:
        pass

    @abstractmethod
    def back_converter(self, data: Any) -> Any:
        pass
