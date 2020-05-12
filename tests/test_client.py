from pytest import fixture, raises

from todoms.client import ResponseError
from todoms.resources import Resource

from .utils.constants import API_BASE


@fixture
def resource_class():
    class FakeResource(Resource):
        ENDPOINT = "fake"
        ATTRIBUTES = ("name",)

    return FakeResource


def test_list_resource_returns_all(client, resource_class, requests_mock):
    requests_mock.get(
        f"{API_BASE}/{resource_class.ENDPOINT}",
        json={"value": [{"name": "res-1"}, {"name": "res-2"}]},
    )
    results = client.list(resource_class)

    assert len(results) == 2
    assert len([r for r in results if r.name == "res-1"]) == 1
    assert len([r for r in results if r.name == "res-2"]) == 1


def test_list_result_raises_on_http_error(client, resource_class, requests_mock):
    requests_mock.get(f"{API_BASE}/{resource_class.ENDPOINT}", status_code=500)

    with raises(ResponseError):
        client.list(resource_class)
