from pytest import fixture, raises, mark

from todoms.client import ResponseError, ResourceNotFoundError
from todoms.resources import Resource

from .utils.constants import API_BASE

EXPECTED_ERRORS = [(404, ResourceNotFoundError), (500, ResponseError)]


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
