import urllib
from datetime import datetime, timezone

import pytest

from todoms.attributes import Content as ContentAttr
from todoms.attributes import Importance, Status
from todoms.fields.basic import Attribute
from todoms.filters import and_, eq
from todoms.recurrence import Recurrence, patterns, ranges
from todoms.resources import (
    Content,
    Resource,
    ResourceAlreadyCreatedError,
    Task,
    TaskList,
    TaskListNotSpecifiedError,
)

from .utils.constants import API_BASE
from .utils.helpers import match_body


@pytest.fixture
def simple_resource_class():
    class SimpleResource(Resource):
        ENDPOINT = "endpoint"
        _id = Attribute("id")
        name = Attribute("name")

    return SimpleResource


TASK_LIST_EXAMPLE_DATA = {
    # "@odata.context": "https://graph.microsoft.com/beta/$metadata#lists/$entity",
    # "@odata.etag": "xxx",
    "displayName": "list-name",
    "isOwner": True,  # TODO:
    "isShared": True,  # TODO:
    "wellknownListName": "none",  # TODO:
    "id": "id-1",
}

TASK_EXAMPLE_DATA = {
    # "@odata.etag": "W/\"SRqIGuHKgEaeKjdSMmaZRwADcFhrVA==\"",
    "importance": "high",
    "isReminderOn": True,
    "reminderDateTime": {"dateTime": "2020-05-03T00:00:00.000000", "timeZone": "UTC"},
    "status": "notStarted",
    "title": "My new task",
    "createdDateTime": "2020-01-01T18:00:00Z",
    "lastModifiedDateTime": "2021-01-01T18:00:00Z",
    "dueDateTime": {"dateTime": "2020-05-02T00:00:00.000000", "timeZone": "UTC"},
    "id": "task-1",
    "body": {"content": "task-body", "contentType": "html"},
    "completedDateTime": {"dateTime": "2020-05-01T00:00:00.000000", "timeZone": "UTC"},
    "recurrence": {
        "pattern": {
            "type": "absoluteYearly",
            "interval": 1,
            "month": 7,
            "dayOfMonth": 5,
        },
        "range": {"type": "noEnd"},
    },
    "categories": ["category-1", "category-2"],
    "hasAttachments": False,
    "startDateTime": {"dateTime": "2020-03-02T00:00:00.000000", "timeZone": "UTC"},
}


@pytest.fixture
def task_list(client):
    return TaskList.from_dict(client, TASK_LIST_EXAMPLE_DATA)


@pytest.mark.parametrize(
    "resource,endpoint",
    [(TaskList, "todo/lists"), (Task, "tasks")],
)
def test_resource_has_proper_endpoint(resource, endpoint):
    assert resource.ENDPOINT == endpoint


@pytest.mark.parametrize(
    "resource,data,to_omit",
    [(TaskList, TASK_LIST_EXAMPLE_DATA, ["isShared"]), (Task, TASK_EXAMPLE_DATA, [])],
)
def test_resource_is_proper_converted_back_to_dict(resource, data, to_omit):
    obj = resource.from_dict(None, data)
    expected = {k: v for k, v in data.items() if k not in to_omit}
    assert expected == obj.to_dict()


class TestDefaultResource:
    def test_default_resource_create_set_client(self, client, simple_resource_class):
        resource = simple_resource_class.from_dict(
            client, {"_id": "id-1", "name": "name-1"}
        )

        assert resource._client == client
        assert resource.name == "name-1"

    def test_default_resource_update_client_call_and_refresh_data_from_response(
        self, client, requests_mock
    ):
        class ComplexResource(Resource):
            ENDPOINT = "fake"
            _id = Attribute("id")
            new = Content("old")
            last_updated = Attribute("last_updated")

        resource = ComplexResource(client, new=ContentAttr("data"), _id="id-1")

        requests_mock.patch(
            f"{API_BASE}/fake/id-1",
            json={"last_updated": "2020-01-01T18:00:00Z"},
            status_code=200,
            additional_matcher=match_body(resource.to_dict()),
        )

        resource.update()
        assert requests_mock.called is True
        assert resource.last_updated == "2020-01-01T18:00:00Z"

    def test_default_resource_refresh_clearing_old_data(self, client, requests_mock):
        class ComplexResource(Resource):
            ENDPOINT = "fake"
            _id = Attribute("id")
            new = Attribute("old")
            to_clear = Attribute("to_clear")
            last_updated = Attribute("last_updated", read_only=True)

        resource = ComplexResource(client, new="data", _id="id-1", to_clear="data")

        requests_mock.get(
            f"{API_BASE}/fake/id-1",
            json={
                "last_updated": "2020-01-01T18:00:00Z",
                "id": "id-1",
                "old": "new-data",
            },
            status_code=200,
        )

        resource.refresh()

        assert resource.new == "new-data"
        assert resource.last_updated == "2020-01-01T18:00:00Z"
        assert resource.id == "id-1"
        assert resource.to_clear is None

    def test_default_resource_id(self, simple_resource_class):
        resource = simple_resource_class.from_dict(
            None, {"id": "id-1", "name": "name-1"}
        )

        assert resource.id == "id-1"

    def test_resources_are_equal_when_have_equal_id(self, simple_resource_class):
        resource_1 = simple_resource_class.from_dict(None, {"id": "id-1"})
        resource_2 = simple_resource_class.from_dict(None, {"id": "id-1"})

        assert resource_1 == resource_2

    def test_resources_are_not_equal_when_have_different_id(
        self, simple_resource_class
    ):
        resource_1 = simple_resource_class.from_dict(None, {"id": "id-1"})
        resource_2 = simple_resource_class.from_dict(None, {"id": "id-2"})

        assert resource_1 != resource_2

    def test_resources_are_not_equal_when_dont_have_id(self, simple_resource_class):
        resource_1 = simple_resource_class.from_dict(None, {"name": "name-1"})
        resource_2 = simple_resource_class.from_dict(None, {"name": "name-1"})

        assert resource_1 != resource_2

    def test_default_resource_managing_endpoint(self, simple_resource_class):
        resource = simple_resource_class.from_dict(
            None, {"id": "id-1", "name": "name-1"}
        )

        assert resource.managing_endpoint == "endpoint/id-1"

    def test_default_resource_id_return_none_when_unset(self, simple_resource_class):
        resource = simple_resource_class.from_dict(None, {"name": "name-1"})

        assert resource.id is None

    def test_default_resource_create_fails_when_id_set(self, simple_resource_class):
        resource = simple_resource_class.from_dict(
            None, {"id": "id-1", "name": "name-1"}
        )

        with pytest.raises(ResourceAlreadyCreatedError):
            resource.create()

    def test_default_resource_create_calls_endpoint(
        self, simple_resource_class, client, requests_mock
    ):
        resource = simple_resource_class(client, name="new-resource")
        requests_mock.post(
            f"{API_BASE}/endpoint",
            json={"id": "new-id", "name": "new-resource"},
            status_code=201,
            additional_matcher=match_body({"name": "new-resource"}),
        )

        resource.create()

        assert requests_mock.called is True
        assert resource.id == "new-id"

    def test_default_resource_delete_calls_endpoint(
        self, simple_resource_class, client, requests_mock
    ):
        resource = simple_resource_class.from_dict(
            client, {"id": "id-1", "name": "name-1"}
        )
        requests_mock.delete(f"{API_BASE}/endpoint/id-1", status_code=204)

        resource.delete()

        assert requests_mock.called is True

    def test_default_handle_list_filter_when_empty(self, simple_resource_class):
        assert simple_resource_class.handle_list_filters() == {}

    def test_default_handle_list_filter_when_given(self, simple_resource_class):
        expected = {
            "$filter": (
                "((key1 eq 'val1' and key2 eq 'val2') and status eq 'inProgress')"
            )
        }
        assert (
            simple_resource_class.handle_list_filters(
                and_(key1=eq("val1"), key2=eq("val2")), status=eq(Status.IN_PROGRESS)
            )
            == expected
        )

    def test_default_handle_list_filter_when_parameter_none(
        self, simple_resource_class: Resource
    ):
        assert simple_resource_class.handle_list_filters(status=None) == {}


class TestTaskListResource:
    def test_create_tasklist_object_from_data(
        self,
    ):
        task_list = TaskList.from_dict(None, TASK_LIST_EXAMPLE_DATA)

        assert task_list.id == "id-1"
        assert task_list.name == "list-name"
        assert task_list.is_owner is True
        assert task_list.is_shared is True
        assert task_list.well_known_name == "none"

    def test_tasklist_get_tasks_returns_default_not_completed_tasks(
        self, client, requests_mock
    ):
        qs = urllib.parse.urlencode({"$filter": "status ne 'completed'"})
        requests_mock.get(
            f"{API_BASE}/todo/lists/id-1/tasks?{qs}",
            json={"value": [TASK_EXAMPLE_DATA]},
            complete_qs=True,
        )
        task_list = TaskList.from_dict(client, TASK_LIST_EXAMPLE_DATA)
        tasks = task_list.get_tasks()

        assert len(tasks) == 1
        assert tasks[0].id == "task-1"
        assert tasks[0].task_list == task_list

    def test_task_list_delete_themselves(self, requests_mock, client):
        requests_mock.delete(f"{API_BASE}/todo/lists/id-1", status_code=204)
        task_list = TaskList.from_dict(client, TASK_LIST_EXAMPLE_DATA)
        task_list.delete()
        assert requests_mock.called is True

    def test_task_list_saves_task(self, requests_mock, client):
        task_list = TaskList.from_dict(client, TASK_LIST_EXAMPLE_DATA)
        new_task = Task(client, title="Test")

        expected_body = {k: v for k, v in new_task.to_dict().items() if v is not None}
        requests_mock.post(
            f"{API_BASE}/todo/lists/id-1/tasks",
            status_code=201,
            json={"id": "new_id"},
            additional_matcher=match_body(expected_body),
        )

        task_list.save_task(new_task)

        assert new_task.task_list is task_list
        assert new_task.id == "new_id"
        assert requests_mock.called is True


class TestTaskResource:
    def test_minimum_task(self):
        task = Task(None, title="Title")

        assert task.id is None
        assert task.title == "Title"
        assert task.task_list is None

        # Default values
        assert task.status == Status.NOT_STARTED
        assert task.importance == Importance.NORMAL
        assert task.is_reminder_on is False
        assert task.body is None
        assert task.recurrence is None
        assert task.due_datetime is None
        assert task.completed_datetime is None
        assert task.last_modified_datetime is None
        assert task.created_datetime is None
        assert task.reminder_datetime is None
        assert task.start_datetime is None
        assert task.categories is None
        assert task.has_attachments is False

    def test_create_task_object_from_dict(self):
        task = Task.from_dict(None, TASK_EXAMPLE_DATA)

        assert task.id == "task-1"
        assert task.body == ContentAttr("task-body")
        assert task.status == Status.NOT_STARTED
        assert task.title == "My new task"
        assert task.importance == Importance.HIGH
        assert task.is_reminder_on is True
        assert task.has_attachments is False
        assert task.task_list is None
        assert task.categories == ["category-1", "category-2"]
        assert task.last_modified_datetime == datetime(
            2021, 1, 1, 18, tzinfo=timezone.utc
        )
        assert task.created_datetime == datetime(2020, 1, 1, 18, tzinfo=timezone.utc)
        assert task.completed_datetime == datetime(2020, 5, 1, tzinfo=timezone.utc)
        assert task.due_datetime == datetime(2020, 5, 2, tzinfo=timezone.utc)
        assert task.reminder_datetime == datetime(2020, 5, 3, tzinfo=timezone.utc)
        assert task.start_datetime == datetime(2020, 3, 2, tzinfo=timezone.utc)
        assert isinstance(task.recurrence, Recurrence) is True
        assert isinstance(task.recurrence.pattern, patterns.YearlyAbsolute)
        assert isinstance(task.recurrence.range, ranges.NoEnd)

    def test_task_handle_filters_default_completed(self):
        filters = Task.handle_list_filters()
        assert filters == {"$filter": "status ne 'completed'"}

    def test_task_handle_filters_select_status(self):
        filters = Task.handle_list_filters(status="my-filter")
        assert filters == {"$filter": "status my-filter"}

    def test_task_delete_themselves(self, requests_mock, client, task_list):
        requests_mock.delete(
            f"{API_BASE}/todo/lists/id-1/tasks/task-1", status_code=204
        )
        task = Task.from_dict(client, TASK_EXAMPLE_DATA)
        task.task_list = task_list

        task.delete()

        assert requests_mock.called is True

    def test_task_create_raises_when_no_tasklist_id(self):
        task = Task(None, title="Test")

        with pytest.raises(TaskListNotSpecifiedError):
            task.create()

    def test_task_managing_endpoint_raises_when_no_tasklist_id(self):
        task = Task(None, title="Test")

        with pytest.raises(TaskListNotSpecifiedError):
            task.managing_endpoint
