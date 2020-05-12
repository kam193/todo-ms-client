from requests import codes

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
        self._url = f"{api_url}/{api_prefix}"  # TODO: safe concatenation

    def list(self, resource_type: Resource):
        url = f"{self._url}/{resource_type.ENDPOINT}"

        response = self._provider.get(url)

        if response.status_code != codes.ok:
            raise ResponseError(response)

        return [resource_type(self, **element) for element in response.json()["value"]]


class ResponseError(Exception):
    """Response returned an error"""

    def __init__(self, response):
        self.response = response

    def __str__(self):
        details = f"{self.response.status_code} {self.response.reason}"
        return f"Server returned an error: {details}"
