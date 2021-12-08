import urllib
from datetime import datetime, timezone

import pytest
from todoms.attributes import Importance, Status
from todoms.filters import and_, eq
from todoms.recurrence import Recurrence, patterns, ranges
from todoms.resources import (
    ContentAttrConverter,
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
        ATTRIBUTES = ("_id", "name")

        def __init__(self, client, name):
            super().__init__(client)
            self.name = name

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
        "range": {"type": "noEnd", "startDate": "2020-07-05"},
    },
}


@pytest.fixture
def task_list(client):
    return TaskList.create_from_dict(client, TASK_LIST_EXAMPLE_DATA)


@pytest.mark.parametrize(
    "resource,endpoint", [(TaskList, "todo/lists"), (Task, "tasks")],
)
def test_resource_has_proper_endpoint(resource, endpoint):
    assert resource.ENDPOINT == endpoint


@pytest.mark.parametrize(
    "resource,data", [(TaskList, TASK_LIST_EXAMPLE_DATA), (Task, TASK_EXAMPLE_DATA)],
)
def test_resource_is_proper_converted_back_to_dict(resource, data):
    obj = resource.create_from_dict(None, data)
    assert data == obj.to_dict()


class TestDefaultResource:
    def test_default_resource_create_set_client(self, client, simple_resource_class):
        resource = simple_resource_class.create_from_dict(
            client, {"_id": "id-1", "name": "name-1"}
        )

        assert resource._client == client
        assert resource.name == "name-1"

    def test_default_resource_update_client_call(self, client, requests_mock):
        class ComplexResource(Resource):
            ENDPOINT = "fake"
            ATTRIBUTES = (ContentAttrConverter("old", "new"), "id")

            def __init__(self, client, new, id):
                super().__init__(client)
                self.new = new
                self._id = id

        resource = ComplexResource(client, new="data", id="id-1")

        requests_mock.patch(
            f"{API_BASE}/fake/id-1",
            json={},
            status_code=200,
            additional_matcher=match_body(resource.to_dict()),
        )

        resource.update()
        assert requests_mock.called is True

    def test_default_resource_id(self, simple_resource_class):
        resource = simple_resource_class.create_from_dict(
            None, {"_id": "id-1", "name": "name-1"}
        )

        assert resource.id == "id-1"

    def test_default_resource_managing_endpoint(self, simple_resource_class):
        resource = simple_resource_class.create_from_dict(
            None, {"_id": "id-1", "name": "name-1"}
        )

        assert resource.managing_endpoint == "endpoint/id-1"

    def test_default_resource_id_return_none_when_unset(self, simple_resource_class):
        resource = simple_resource_class.create_from_dict(None, {"name": "name-1"})

        assert resource.id is None

    def test_default_resource_create_fails_when_id_set(self, simple_resource_class):
        resource = simple_resource_class.create_from_dict(
            None, {"_id": "id-1", "name": "name-1"}
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
        resource = simple_resource_class.create_from_dict(
            client, {"_id": "id-1", "name": "name-1"}
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
    def test_create_tasklist_object_from_data(self,):
        task_list = TaskList.create_from_dict(None, TASK_LIST_EXAMPLE_DATA)

        assert task_list.id == "id-1"
        assert task_list.name == "list-name"
        assert task_list._is_owner is True
        assert task_list._is_shared is True
        assert task_list._well_known_name == "none"

    def test_tasklist_get_tasks_returns_default_not_completed_tasks(
        self, client, requests_mock
    ):
        qs = urllib.parse.urlencode({"$filter": "status ne 'completed'"})
        requests_mock.get(
            f"{API_BASE}/todo/lists/id-1/tasks?{qs}",
            json={"value": [TASK_EXAMPLE_DATA]},
            complete_qs=True,
        )
        task_list = TaskList.create_from_dict(client, TASK_LIST_EXAMPLE_DATA)
        tasks = task_list.get_tasks()

        assert len(tasks) == 1
        assert tasks[0].id == "task-1"
        assert tasks[0].task_list == task_list

    def test_task_list_delete_themselfs(self, requests_mock, client):
        requests_mock.delete(f"{API_BASE}/todo/lists/id-1", status_code=204)
        task_list = TaskList.create_from_dict(client, TASK_LIST_EXAMPLE_DATA)
        task_list.delete()
        assert requests_mock.called is True

    def test_task_list_saves_task(self, requests_mock, client):
        task_list = TaskList.create_from_dict(client, TASK_LIST_EXAMPLE_DATA)
        new_task = Task(client, "Test")

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
        task = Task(None, "Title")

        assert task.id is None
        assert task.title == "Title"
        assert task.task_list is None

    def test_create_task_object_from_dict(self):
        task = Task.create_from_dict(None, TASK_EXAMPLE_DATA)

        assert task.id == "task-1"
        assert task.body == "task-body"
        assert task.status == Status.NOT_STARTED
        assert task.title == "My new task"
        assert task.importance == Importance.HIGH
        assert task.is_reminder_on is True
        assert task.task_list is None
        assert task.last_modified_datetime == datetime(
            2021, 1, 1, 18, tzinfo=timezone.utc
        )
        assert task.created_datetime == datetime(2020, 1, 1, 18, tzinfo=timezone.utc)
        assert task.completed_datetime == datetime(2020, 5, 1, tzinfo=timezone.utc)
        assert task.due_datetime == datetime(2020, 5, 2, tzinfo=timezone.utc)
        assert task.reminder_datetime == datetime(2020, 5, 3, tzinfo=timezone.utc)
        assert isinstance(task.recurrence, Recurrence) is True
        assert isinstance(task.recurrence.pattern, patterns.YearlyAbsolute)
        assert isinstance(task.recurrence.range, ranges.NoEnd)

    def test_task_handle_filters_default_completed(self):
        filters = Task.handle_list_filters()
        assert filters == {"$filter": "status ne 'completed'"}

    def test_task_handle_filters_select_status(self):
        filters = Task.handle_list_filters(status="my-filter")
        assert filters == {"$filter": "status my-filter"}

    def test_task_delete_themselfs(self, requests_mock, client, task_list):
        requests_mock.delete(
            f"{API_BASE}/todo/lists/id-1/tasks/task-1", status_code=204
        )
        task = Task.create_from_dict(client, TASK_EXAMPLE_DATA)
        task.task_list = task_list

        task.delete()

        assert requests_mock.called is True

    def test_task_create_raises_when_no_tasklist_id(self):
        task = Task(None, "Test")

        with pytest.raises(TaskListNotSpecifiedError):
            task.create()

    def test_task_managing_endpoint_raises_when_no_tasklist_id(self):
        task = Task(None, "Test")

        with pytest.raises(TaskListNotSpecifiedError):
            task.managing_endpoint
