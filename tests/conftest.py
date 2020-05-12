from pytest import fixture

from todoms.client import ToDoClient

from .utils.constants import API_PREFIX, API_URL
from .utils.requests_provider import RequestsProvider


@fixture
def client():
    client = ToDoClient(RequestsProvider(), api_url=API_URL, api_prefix=API_PREFIX)
    return client
