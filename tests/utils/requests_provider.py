import requests

from todoms.provider import AbstractProvider


class RequestsProvider(AbstractProvider):
    def get(self, *args, **kwargs):
        return requests.get(*args, **kwargs)
