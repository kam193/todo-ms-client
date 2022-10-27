import os

import pytest

from todoms.client import ToDoClient
from todoms.provider import WebBrowserProvider


@pytest.fixture(scope="session")
def client():
    APP_ID = os.environ.get("APP_ID")
    APP_SECRET = os.environ.get("APP_SECRET")
    TEST_USER_EMAIL = os.environ.get("TEST_USER_EMAIL")

    assert APP_ID and APP_SECRET, "APP_ID and APP_SECRET must be set"
    assert TEST_USER_EMAIL, "TEST_USER_EMAIL must be set"

    provider = WebBrowserProvider(APP_ID, APP_SECRET)
    provider.authorize(local_port=8000)

    user_data = provider.get("https://graph.microsoft.com/v1.0/me").json()
    assert user_data["userPrincipalName"] == TEST_USER_EMAIL

    client = ToDoClient(provider)
    return client
