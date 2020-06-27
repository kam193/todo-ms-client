from typing import Type

from furl import furl
from requests import Response, codes

from .provider import AbstractProvider
from .resources import Resource


class ToDoClient(object):
    def __init__(
        self,
        provider: AbstractProvider,
        api_url: str = "https://graph.microsoft.com/beta",
        api_prefix: str = "me",
    ):
        self._provider = provider
        self._url = furl(api_url) / api_prefix

    def list(self, resource_class: Type[Resource], endpoint: str = None, **kwargs):
        url = (self._url / (endpoint or resource_class.ENDPOINT)).url
        params = resource_class.handle_list_filters(**kwargs)

        elements = []
        while url:
            response = self._provider.get(url, params=params)
            self._map_http_errors(response, codes.ok)
            data = response.json()
            elements += data["value"]
            url = data.get("@odata.nextLink", None)
            params = {}

        return [resource_class.create_from_dict(self, element) for element in elements]

    def get(self, resource_class: Type[Resource], resource_id: str):
        url = (self._url / resource_class.ENDPOINT / resource_id).url
        response = self._provider.get(url)
        self._map_http_errors(response, codes.ok)
        return resource_class.create_from_dict(self, response.json())

    def delete(self, resource: Resource):
        url = (self._url / resource.managing_endpoint).url
        response = self._provider.delete(url)
        self._map_http_errors(response, codes.no_content)

    def patch(self, resource: Resource):
        url = (self._url / resource.managing_endpoint).url
        response = self._provider.patch(url, json_data=resource.to_dict())
        self._map_http_errors(response, codes.ok)
        return response.json()

    def raw_post(self, endpoint: str, data: dict, expected_code: int = codes.created):
        url = (self._url / endpoint).url
        response = self._provider.post(url, json_data=data)
        self._map_http_errors(response, expected_code)
        return response.json()

    def _map_http_errors(self, response, expected):
        if response.status_code == codes.not_found:
            raise ResourceNotFoundError(response)

        if response.status_code != expected:
            raise ResponseError(response)


class ResponseError(Exception):
    """Response returned an error"""

    MESSAGE = None

    def __init__(self, response: Response):
        self.response = response

    def __str__(self):
        if self.MESSAGE:
            return self.MESSAGE

        details = f"{self.response.status_code} {self.response.reason}"
        return f"Server returned an error: {details}"


class ResourceNotFoundError(ResponseError):
    """Requested resource not exists"""

    MESSAGE = "404 Resource not found"
