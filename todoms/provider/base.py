from abc import ABC, abstractmethod

from requests import Response


class AbstractProvider(ABC):
    @abstractmethod
    def get(url: str, params: dict) -> Response:
        pass
