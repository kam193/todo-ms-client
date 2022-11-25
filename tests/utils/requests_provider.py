import requests

from todoms.provider import AbstractProvider


class RequestsProvider(AbstractProvider):
    def _validate_url_is_str(self, url):
        """oauthlib used typically as a provider requires url to be a string"""
        if not isinstance(url, str):
            raise TypeError("url must be a string")

    def get(self, url, params=None):
        self._validate_url_is_str(url)
        return requests.get(url=url, params=params)

    def delete(self, url):
        self._validate_url_is_str(url)
        return requests.delete(url=url)

    def patch(self, url, json_data):
        self._validate_url_is_str(url)
        return requests.patch(url=url, json=json_data)

    def post(self, url, json_data):
        self._validate_url_is_str(url)
        return requests.post(url=url, json=json_data)
