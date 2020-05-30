import requests

from todoms.provider import AbstractProvider


class RequestsProvider(AbstractProvider):
    def get(self, url, params=None):
        return requests.get(url=url, params=params)

    def delete(self, url):
        return requests.delete(url=url)

    def patch(self, url, json_data):
        return requests.patch(url=url, json=json_data)
