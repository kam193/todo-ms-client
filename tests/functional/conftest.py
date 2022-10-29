import logging
import os
from collections import Counter
from uuid import uuid4

import pytest

from todoms.client import ToDoClient
from todoms.provider import WebBrowserProvider

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def provider():
    APP_ID = os.environ.get("APP_ID")
    APP_SECRET = os.environ.get("APP_SECRET")
    TEST_USER_EMAIL = os.environ.get("TEST_USER_EMAIL")

    assert APP_ID and APP_SECRET, "APP_ID and APP_SECRET must be set"
    assert TEST_USER_EMAIL, "TEST_USER_EMAIL must be set"

    provider = WebBrowserProvider(APP_ID, APP_SECRET)
    provider.authorize(local_port=8000)

    user_data = provider.get("https://graph.microsoft.com/v1.0/me").json()
    assert user_data["userPrincipalName"] == TEST_USER_EMAIL

    return provider


@pytest.fixture(scope="session")
def client(provider):
    client = ToDoClient(provider)
    return client


@pytest.fixture(scope="session")
def run_id():
    return uuid4().hex


@pytest.fixture(scope="session")
def counter():
    return Counter()


@pytest.fixture
def generate_id(run_id, counter):
    def _generate_id(name):
        counter[name] += 1
        return f"{name}-{counter[name]}-{run_id}"

    return _generate_id


@pytest.fixture
def clean_up(provider, client):
    to_clean_up = list()

    def _clean_up(resource):
        to_clean_up.append(str(client._url / resource.managing_endpoint))

    yield _clean_up

    for url in to_clean_up:
        try:
            provider.delete(url)
        except Exception:
            logger.warning("Could not clean up %s: %s", url, exc_info=True)
