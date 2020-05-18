from pytest import fixture, mark, raises

from todoms.client import ResourceNotFoundError, ResponseError
from todoms.resources import Resource

from .utils.constants import API_BASE

EXPECTED_ERRORS = [(404, ResourceNotFoundError), (500, ResponseError)]


@fixture
def resource_class():
    class FakeResource(Resource):
        ENDPOINT = "fake"
        ATTRIBUTES = ("name",)

        @classmethod
        def handle_list_filters(cls, **kwargs):
            return {name: f"{value}-parsed" for name, value in kwargs.items()}

    return FakeResource


def test_list_resource_returns_all(client, resource_class, requests_mock):
    requests_mock.get(
        f"{API_BASE}/{resource_class.ENDPOINT}",
        json={"value": [{"name": "res-1"}, {"name": "res-2"}]},
    )
    results = client.list(resource_class)

    assert len(results) == 2
    assert list(filter(lambda e: e.name == "res-1", results)) is not []
    assert list(filter(lambda e: e.name == "res-2", results)) is not []


def test_list_resource_returns_all_when_parted(client, resource_class, requests_mock):
    requests_mock.get(
        f"{API_BASE}/{resource_class.ENDPOINT}",
        json={"value": [{"name": "res-1"}], "@odata.nextLink": "http://next/part/1"},
    )
    requests_mock.get(
        "http://next/part/1",
        json={"value": [{"name": "res-2"}], "@odata.nextLink": "http://next/part/2"},
    )
    requests_mock.get(
        "http://next/part/2", json={"value": [{"name": "res-3"}]},
    )

    results = client.list(resource_class)
    assert len(results) == 3
    assert list(filter(lambda e: e.name == "res-1", results)) is not []
    assert list(filter(lambda e: e.name == "res-2", results)) is not []
    assert list(filter(lambda e: e.name == "res-3", results)) is not []


def test_list_use_custom_endpoint(client, resource_class, requests_mock):
    requests_mock.get(
        f"{API_BASE}/my-endpoint/all", json={"value": [{"name": "res-1"}]},
    )

    results = client.list(resource_class, endpoint="my-endpoint/all")
    assert len(results) == 1


def test_list_resources_sends_filters(client, resource_class, requests_mock):
    requests_mock.get(
        f"{API_BASE}/{resource_class.ENDPOINT}?filter=test-parsed",
        json={"value": [{"name": "res-1"}], "@odata.nextLink": "http://next/part/1"},
    )
    requests_mock.get(
        "http://next/part/1", json={"value": [{"name": "res-2"}]},
    )

    results = client.list(resource_class, filter="test")
    assert len(results) == 2
    assert list(filter(lambda e: e.name == "res-1", results)) is not []
    assert list(filter(lambda e: e.name == "res-2", results)) is not []


@mark.parametrize("error_code,exception", EXPECTED_ERRORS)
def test_list_resource_raises_on_http_error(
    client, resource_class, requests_mock, error_code, exception
):
    requests_mock.get(f"{API_BASE}/{resource_class.ENDPOINT}", status_code=error_code)

    with raises(exception):
        client.list(resource_class)


def test_get_resource_returns_obj(client, resource_class, requests_mock):
    requests_mock.get(
        f"{API_BASE}/{resource_class.ENDPOINT}/id-1", json={"name": "res-1"},
    )
    result = client.get(resource_class, "id-1")

    assert result.name == "res-1"
    assert isinstance(result, resource_class)


@mark.parametrize("error_code,exception", EXPECTED_ERRORS)
def test_get_resource_raises_on_http_error(
    client, resource_class, requests_mock, error_code, exception
):
    requests_mock.get(
        f"{API_BASE}/{resource_class.ENDPOINT}/fail", status_code=error_code
    )

    with raises(exception):
        client.get(resource_class, "fail")
