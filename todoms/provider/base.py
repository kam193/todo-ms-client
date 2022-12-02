from abc import ABC, abstractmethod
from typing import Optional

from requests import Response


class AbstractProvider(ABC):
    @abstractmethod
    def get(self, url: str, params: Optional[dict] = None) -> Response:
        pass

    @abstractmethod
    def delete(self, url: str) -> Response:
        pass

    @abstractmethod
    def patch(self, url: str, json_data: dict) -> Response:
        pass

    @abstractmethod
    def post(self, url: str, json_data: dict) -> Response:
        pass
