import logging
from typing import Any, Iterable, Optional, Type, TypeVar

from furl import furl  # type: ignore
from requests import Response, codes

from .provider import AbstractProvider
from .resources import Resource, TaskList

logger = logging.getLogger(__name__)


class ResponseError(Exception):
    """Response returned an error"""

    MESSAGE: Optional[str] = None

    def __init__(self, response: Response) -> None:
        self.response = response

    def __str__(self) -> str:
        if self.MESSAGE:
            return self.MESSAGE

        details = f"{self.response.status_code} {self.response.reason}"
        return f"Server returned an error: {details}"


class ResourceNotFoundError(ResponseError):
    """Requested resource not exists"""

    MESSAGE = "404 Resource not found"


ResourceType = TypeVar("ResourceType", bound=Resource)


class ToDoClient:
    def __init__(
        self,
        provider: AbstractProvider,
        api_url: str = "https://graph.microsoft.com/beta",
        api_prefix: str = "me",
    ):
        self._provider = provider
        self._url = furl(api_url) / api_prefix

    def _map_http_errors(self, response: Response, expected: int) -> None:
        logger.debug(
            "Got response with code %s: %s",
            response.status_code,
            response.text,
        )

        if response.status_code == codes.not_found:
            raise ResourceNotFoundError(response)

        if response.status_code != expected:
            logger.warning(
                "Unexpected response %s: %s", response.status_code, response.text
            )
            raise ResponseError(response)

    def list(
        self,
        resource_class: Type[ResourceType],
        endpoint: Optional[str] = None,
        delta: bool = True,
        **kwargs: Any,
    ) -> Iterable[ResourceType]:
        url = self._url / (endpoint or resource_class.ENDPOINT)
        params = resource_class.handle_list_filters(**kwargs)

        if delta and not params:
            url = url / "delta"
        if delta and params:
            logger.info("Requested delta query with filter, skipping delta")

        url = url.url  # Translate furl to str
        while url:
            logger.debug("Listing %s", url)
            response = self._provider.get(url, params=params)
            self._map_http_errors(response, codes.ok)
            data = response.json()
            if not data:
                return
            url = data.get("@odata.nextLink", None)
            params = {}
            for element in data["value"]:
                yield resource_class.from_dict(element, client=self)

    def get(
        self,
        resource_class: Type[ResourceType],
        resource_id: Optional[str] = None,
        endpoint: Optional[str] = None,
    ) -> ResourceType:
        if not endpoint and not resource_id:
            raise ValueError("Either endpoint or resource_id must be provided")

        endpoint = endpoint or f"{resource_class.ENDPOINT}/{resource_id}"
        response = self.raw_get(endpoint)
        return resource_class.from_dict(response, client=self)

    def raw_get(self, endpoint: str) -> dict:
        url = (self._url / endpoint).url
        logger.debug("Getting %s", url)
        response = self._provider.get(url)
        self._map_http_errors(response, codes.ok)
        return response.json()  # type: ignore

    def delete(self, resource: Resource) -> None:
        url = (self._url / resource.managing_endpoint).url
        logger.debug("Deleting %s", url)
        response = self._provider.delete(url)
        self._map_http_errors(response, codes.no_content)

    def patch(self, resource: Resource) -> dict:
        url = (self._url / resource.managing_endpoint).url

        data = resource.to_dict()
        response = self._provider.patch(url, json_data=data)
        logger.debug("Patching %s", url, extra={"data": data})
        self._map_http_errors(response, codes.ok)
        return response.json()  # type: ignore

    def raw_post(
        self, endpoint: str, data: dict, expected_code: int = codes.created
    ) -> dict:
        url = (self._url / endpoint).url
        logger.debug("Posting %s", url, extra={"data": data})
        response = self._provider.post(url, json_data=data)
        self._map_http_errors(response, expected_code)
        return response.json()  # type: ignore

    @property
    def task_lists(self) -> Iterable[TaskList]:
        return self.list(TaskList)

    def save_list(self, task_list: TaskList) -> TaskList:
        task_list._client = self
        task_list.create()
        return task_list
