from pytest import fixture, mark, raises

from todoms.client import ResourceNotFoundError, ResponseError
from todoms.fields.basic import Attribute
from todoms.resources import Resource

from .utils.constants import API_BASE
from .utils.helpers import match_body

EXPECTED_ERRORS = [(404, ResourceNotFoundError), (500, ResponseError)]


@fixture
def resource_class():
    class FakeResource(Resource):
        ENDPOINT = "fake"
        _id = Attribute("id")
        name = Attribute("name")

        @classmethod
        def handle_list_filters(cls, **kwargs):
            return {name: f"{value}-parsed" for name, value in kwargs.items()}

    return FakeResource


@fixture
def resource_obj(resource_class):
    return resource_class(None, name="name-1", _id="id-1")


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
        "http://next/part/2",
        json={"value": [{"name": "res-3"}]},
    )

    results = client.list(resource_class)
    assert len(results) == 3
    assert list(filter(lambda e: e.name == "res-1", results)) is not []
    assert list(filter(lambda e: e.name == "res-2", results)) is not []
    assert list(filter(lambda e: e.name == "res-3", results)) is not []


def test_list_use_custom_endpoint(client, resource_class, requests_mock):
    requests_mock.get(
        f"{API_BASE}/my-endpoint/all",
        json={"value": [{"name": "res-1"}]},
    )

    results = client.list(resource_class, endpoint="my-endpoint/all")
    assert len(results) == 1


def test_list_resources_sends_filters(client, resource_class, requests_mock):
    requests_mock.get(
        f"{API_BASE}/{resource_class.ENDPOINT}?filter=test-parsed",
        json={"value": [{"name": "res-1"}], "@odata.nextLink": "http://next/part/1"},
    )
    requests_mock.get(
        "http://next/part/1",
        json={"value": [{"name": "res-2"}]},
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
        f"{API_BASE}/{resource_class.ENDPOINT}/id-1",
        json={"name": "res-1"},
    )
    result = client.get(resource_class, "id-1")

    assert result.name == "res-1"
    assert isinstance(result, resource_class)


def test_get_uses_provided_endpoint(client, resource_class, requests_mock):
    requests_mock.get(
        f"{API_BASE}/precreated-endpoint",
        json={"name": "res-1"},
    )
    result = client.get(resource_class, endpoint="precreated-endpoint")

    assert result.name == "res-1"
    assert isinstance(result, resource_class)


def test_get_raises_when_not_endpint_and_id(client, resource_class):
    with raises(ValueError):
        client.get(resource_class)


@mark.parametrize("error_code,exception", EXPECTED_ERRORS)
def test_get_resource_raises_on_http_error(
    client, resource_class, requests_mock, error_code, exception
):
    requests_mock.get(
        f"{API_BASE}/{resource_class.ENDPOINT}/fail", status_code=error_code
    )

    with raises(exception):
        client.get(resource_class, "fail")


def test_delete_resource_pass(client, resource_obj, requests_mock):
    requests_mock.delete(f"{API_BASE}/{resource_obj.ENDPOINT}/id-1", status_code=204)
    client.delete(resource_obj)


@mark.parametrize("error_code,exception", EXPECTED_ERRORS)
def test_delete_resource_raises_on_http_error(
    client, resource_obj, requests_mock, error_code, exception
):
    requests_mock.delete(
        f"{API_BASE}/{resource_obj.ENDPOINT}/id-1", status_code=error_code
    )

    with raises(exception):
        client.delete(resource_obj)


@mark.parametrize("error_code,exception", EXPECTED_ERRORS)
def test_patch_resource_raises_on_http_error(
    client, resource_obj, requests_mock, error_code, exception
):
    requests_mock.patch(
        f"{API_BASE}/{resource_obj.ENDPOINT}/id-1", status_code=error_code
    )

    with raises(exception):
        client.patch(resource_obj)


def test_patch_sends_data(client, resource_obj, requests_mock):
    requests_mock.patch(
        f"{API_BASE}/{resource_obj.ENDPOINT}/id-1",
        json={"ok": "true"},
        additional_matcher=match_body({"name": "name-1", "id": "id-1"}),
    )

    response = client.patch(resource_obj)

    assert response == {"ok": "true"}


def test_raw_post(client, requests_mock):
    requests_mock.post(
        f"{API_BASE}/my-endpoint/sendind",
        json={"result": "ok"},
        status_code=201,
        additional_matcher=match_body({"my": "body"}),
    )
    result = client.raw_post("my-endpoint/sendind", data={"my": "body"})

    assert result == {"result": "ok"}


def test_raw_post_with_nondefault_status_code(client, requests_mock):
    requests_mock.post(
        f"{API_BASE}/my-endpoint/sendind",
        json={"result": "ok"},
        status_code=205,
        additional_matcher=match_body({"my": "body"}),
    )
    result = client.raw_post(
        "my-endpoint/sendind", data={"my": "body"}, expected_code=205
    )

    assert result == {"result": "ok"}


@mark.parametrize("error_code,exception", EXPECTED_ERRORS)
def test_raw_post_raises_on_error(client, requests_mock, error_code, exception):
    requests_mock.post(
        f"{API_BASE}/my-endpoint/sendind", json={"result": "ok"}, status_code=error_code
    )

    with raises(exception):
        client.raw_post("my-endpoint/sendind", data={})
