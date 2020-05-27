import requests

from todoms.provider import AbstractProvider


class RequestsProvider(AbstractProvider):
    def get(self, *args, **kwargs):
        return requests.get(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return requests.delete(*args, **kwargs)
