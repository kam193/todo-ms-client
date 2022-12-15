import urllib
from datetime import datetime, timezone

import pytest

from todoms.attributes import Content as ContentAttr
from todoms.attributes import Importance, Status
from todoms.client import ToDoClient
from todoms.fields.basic import Attribute
from todoms.filters import and_, eq
from todoms.recurrence import Recurrence, patterns, ranges
from todoms.resources import (
    ContentField,
    Resource,
    ResourceAlreadyCreatedError,
    Subtask,
    Task,
    TaskList,
    TaskListNotSpecifiedError,
    TaskNotSpecifiedError,
    UnsupportedOperationError,
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
    "isOwner": True,
    "isShared": True,
    "wellknownListName": "none",
    "id": "id-1",
}

SUBTASK_EXAMPLE_DATA = {
    "displayName": "Subtask-1",
    "createdDateTime": "2022-12-09T14:03:33Z",
    "isChecked": True,
    "checkedDateTime": "2022-12-09T16:13:52Z",
    "id": "sub-1",
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
    "checklistItems": [SUBTASK_EXAMPLE_DATA],
}


@pytest.fixture
def task_list(client):
    return TaskList.from_dict(TASK_LIST_EXAMPLE_DATA, client=client)


@pytest.fixture
def task(client, task_list):
    t = Task.from_dict(TASK_EXAMPLE_DATA, client=client)
    t.task_list = task_list
    return t


@pytest.mark.parametrize(
    "resource,endpoint",
    [(TaskList, "todo/lists"), (Task, "tasks"), (Subtask, "checklistItems")],
)
def test_resource_has_proper_endpoint(resource, endpoint):
    assert resource.ENDPOINT == endpoint


@pytest.mark.parametrize(
    "resource,data,to_omit",
    [
        (TaskList, TASK_LIST_EXAMPLE_DATA, ["isShared"]),
        (Task, TASK_EXAMPLE_DATA, ["checklistItems"]),
        (Subtask, SUBTASK_EXAMPLE_DATA, ["createdDateTime"]),
    ],
)
def test_resource_is_proper_converted_back_to_dict(resource, data, to_omit, client):
    obj = resource.from_dict(data, client=client)
    expected = {k: v for k, v in data.items() if k not in to_omit}
    assert expected == obj.to_dict()


class TestDefaultResource:
    def test_default_resource_create_set_client(self, client, simple_resource_class):
        resource = simple_resource_class.from_dict(
            {"_id": "id-1", "name": "name-1"}, client=client
        )

        assert resource._client == client
        assert resource.name == "name-1"

    def test_default_resource_update_client_call_and_refresh_data_from_response(
        self, client, requests_mock
    ):
        class ComplexResource(Resource):
            ENDPOINT = "fake"
            _id = Attribute("id")
            new = ContentField("old")
            last_updated = Attribute("last_updated")

        resource = ComplexResource(client=client, new=ContentAttr("data"), _id="id-1")

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

        resource = ComplexResource(
            client=client, new="data", _id="id-1", to_clear="data"
        )

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
        resource = simple_resource_class.from_dict({"id": "id-1", "name": "name-1"})

        assert resource.id == "id-1"

    def test_resources_are_equal_when_have_equal_id(self, simple_resource_class):
        resource_1 = simple_resource_class.from_dict({"id": "id-1"})
        resource_2 = simple_resource_class.from_dict({"id": "id-1"})

        assert resource_1 == resource_2

    def test_resources_are_not_equal_when_have_different_id(
        self, simple_resource_class
    ):
        resource_1 = simple_resource_class.from_dict({"id": "id-1"})
        resource_2 = simple_resource_class.from_dict({"id": "id-2"})

        assert resource_1 != resource_2

    def test_resources_are_not_equal_when_dont_have_id(self, simple_resource_class):
        resource_1 = simple_resource_class.from_dict({"name": "name-1"})
        resource_2 = simple_resource_class.from_dict({"name": "name-1"})

        assert resource_1 != resource_2

    def test_default_resource_managing_endpoint(self, simple_resource_class):
        resource = simple_resource_class.from_dict({"id": "id-1", "name": "name-1"})

        assert resource.managing_endpoint == "endpoint/id-1"

    def test_default_resource_id_return_none_when_unset(self, simple_resource_class):
        resource = simple_resource_class.from_dict({"name": "name-1"})

        assert resource.id is None

    def test_default_resource_create_fails_when_id_set(self, simple_resource_class):
        resource = simple_resource_class.from_dict({"id": "id-1", "name": "name-1"})

        with pytest.raises(ResourceAlreadyCreatedError):
            resource.create()

    def test_default_resource_create_calls_endpoint(
        self, simple_resource_class, client, requests_mock
    ):
        resource = simple_resource_class(client=client, name="new-resource")
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
            {"id": "id-1", "name": "name-1"}, client=client
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
        task_list = TaskList.from_dict(TASK_LIST_EXAMPLE_DATA)

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
        task_list = TaskList.from_dict(TASK_LIST_EXAMPLE_DATA, client=client)
        tasks = list(task_list.get_tasks())

        assert len(tasks) == 1
        assert tasks[0].id == "task-1"
        assert tasks[0].task_list == task_list
        assert tasks == list(task_list.open_tasks)

    def test_tasklist_prop_all_tasks_returns_all(self, client, requests_mock):
        requests_mock.get(
            f"{API_BASE}/todo/lists/id-1/tasks",
            json={"value": [TASK_EXAMPLE_DATA]},
            complete_qs=True,
        )
        task_list = TaskList.from_dict(TASK_LIST_EXAMPLE_DATA, client=client)
        tasks = list(task_list.tasks)

        assert len(tasks) == 1
        assert tasks[0].id == "task-1"
        assert tasks[0].task_list == task_list

    def test_task_list_delete_themselves(self, requests_mock, client):
        requests_mock.delete(f"{API_BASE}/todo/lists/id-1", status_code=204)
        task_list = TaskList.from_dict(TASK_LIST_EXAMPLE_DATA, client=client)
        task_list.delete()
        assert requests_mock.called is True

    def test_task_list_saves_task(self, requests_mock, client):
        task_list = TaskList.from_dict(TASK_LIST_EXAMPLE_DATA, client=client)
        new_task = Task(client=client, title="Test")

        expected_body = {k: v for k, v in new_task.to_dict().items() if v is not None}
        requests_mock.post(
            f"{API_BASE}/todo/lists/id-1/tasks",
            status_code=201,
            json={"id": "new_id"},
            additional_matcher=match_body(expected_body),
        )

        task_list.save_task(new_task)

        assert new_task._task_list is task_list
        assert new_task.id == "new_id"
        assert requests_mock.called is True


class TestTaskResource:
    def test_minimum_task(self):
        task = Task(title="Title")

        assert task.id is None
        assert task.title == "Title"
        assert task._task_list is None

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

    def test_create_task_object_from_dict(self, client):
        task = Task.from_dict(TASK_EXAMPLE_DATA, client=client)

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

        assert len(task.subtasks) == 1
        assert task.subtasks[0].name == "Subtask-1"
        assert task.subtasks[0].task is task

    @staticmethod
    def _default_task_body(title: str, id: str = None):
        data = {
            "title": title,
            "hasAttachments": False,
            "importance": "normal",
            "isReminderOn": False,
            "status": "notStarted",
        }
        if id:
            data["id"] = id
        return data

    def test_create_task_with_subtasks(
        self, client: ToDoClient, requests_mock, task_list: TaskList
    ):
        task = Task(title="Task-1", task_list=task_list, client=client)
        task.add_subtask("Sub-1")

        requests_mock.post(
            f"{API_BASE}/todo/lists/{task_list.id}/tasks",
            status_code=201,
            json={"id": "new-id", "title": "Task-1"},
            additional_matcher=match_body(self._default_task_body("Task-1")),
        )
        requests_mock.post(
            f"{API_BASE}/todo/lists/{task_list.id}/tasks/new-id/checklistItems",
            status_code=201,
            json={"id": "s-1", "displayName": "Sub-1"},
            additional_matcher=match_body({"displayName": "Sub-1", "isChecked": False}),
        )

        task.create()

        assert task.subtasks[0].id == "s-1"

    def test_create_task_without_subtasks(
        self, client: ToDoClient, requests_mock, task_list: TaskList
    ):
        task = Task(title="Task-1", task_list=task_list, client=client)

        requests_mock.post(
            f"{API_BASE}/todo/lists/{task_list.id}/tasks",
            status_code=201,
            json={"id": "new-id", "title": "Task-1"},
            additional_matcher=match_body(self._default_task_body("Task-1")),
        )

        task.create()

        assert task.id == "new-id"

    def test_updating_tasks_updates_and_creates_subtasks(
        self, client: ToDoClient, requests_mock, task_list: TaskList
    ):
        task = Task(title="Task-1", _id="id-1", task_list=task_list, client=client)
        task.add_subtask(
            Subtask(name="Existing", _id="sub-1", task=task, client=client)
        )
        task.add_subtask("new subtask")

        requests_mock.patch(
            f"{API_BASE}/todo/lists/{task_list.id}/tasks/id-1",
            status_code=200,
            json={"id": "id-1", "title": "Task-1"},
        )
        # The already created subtask should be updated
        requests_mock.patch(
            f"{API_BASE}/todo/lists/{task_list.id}/tasks/id-1/checklistItems/sub-1",
            status_code=200,
            json={"id": "sub-1", "displayName": "Existing"},
            additional_matcher=match_body(
                {
                    "displayName": "Existing",
                    "isChecked": False,
                    "id": "sub-1",
                    "checkedDateTime": None,
                }
            ),
        )
        # The new subtask should be created
        requests_mock.post(
            f"{API_BASE}/todo/lists/{task_list.id}/tasks/id-1/checklistItems",
            status_code=201,
            json={"id": "sub-2", "displayName": "new subtask"},
            additional_matcher=match_body(
                {
                    "displayName": "new subtask",
                    "isChecked": False,
                }
            ),
        )

        task.update()

        assert task.subtasks[1].id == "sub-2"

    def test_updating_task_without_subtasks(
        self, client: ToDoClient, requests_mock, task_list: TaskList
    ):
        task = Task(title="Task-1", _id="id-1", task_list=task_list, client=client)
        requests_mock.patch(
            f"{API_BASE}/todo/lists/{task_list.id}/tasks/id-1",
            status_code=200,
            json={"id": "new-id", "title": "Task-1"},
        )
        task.update()

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
        task = Task.from_dict(TASK_EXAMPLE_DATA, client=client)
        task.task_list = task_list

        task.delete()

        assert requests_mock.called is True

    def test_task_create_raises_when_no_tasklist_id(self):
        task = Task(title="Test")

        with pytest.raises(TaskListNotSpecifiedError):
            task.create()

    def test_task_managing_endpoint_raises_when_no_tasklist_id(self):
        task = Task(title="Test")

        with pytest.raises(TaskListNotSpecifiedError):
            task.managing_endpoint

    def test_task_raises_when_try_to_change_list(self, task_list, client):
        task = Task.from_dict(TASK_EXAMPLE_DATA, client=client)
        task.task_list = task_list

        # Allow assign once more the same
        task.task_list = task_list

        task_list_2 = TaskList.from_dict({"id": "id-2"})
        with pytest.raises(UnsupportedOperationError):
            task.task_list = task_list_2

    def test_saving_subtask(self, task, requests_mock):
        subtask = Subtask(name="To Do")
        requests_mock.post(
            f"{API_BASE}/todo/lists/id-1/tasks/task-1/checklistItems",
            status_code=201,
            json={"id": "new-id", "displayName": "To Do"},
            additional_matcher=match_body({"displayName": "To Do", "isChecked": False}),
        )

        task.save_subtask(subtask)

        assert subtask.task is task
        assert subtask.client is task.client
        assert subtask in task.subtasks
        assert subtask.id == "new-id"

    def test_adding_subtask_from_object(self, task):
        subtask = Subtask(name="To Do")

        task.add_subtask(subtask)

        assert subtask.task is task
        assert subtask.client is task.client
        assert subtask in task.subtasks
        assert subtask.id is None

    def test_adding_subtask_from_string(self, task):
        task.add_subtask("My test")

        subtask = next(filter(lambda s: s.name == "My test", task.subtasks))
        assert subtask.task is task
        assert subtask.client is task.client
        assert subtask.id is None


class TestSubtaskResource:
    def test_create_from_dict(self):
        subtask = Subtask.from_dict(SUBTASK_EXAMPLE_DATA)

        assert subtask.name == "Subtask-1"
        assert subtask.is_checked is True
        assert subtask.created_datetime == datetime(
            2022, 12, 9, 14, 3, 33, tzinfo=timezone.utc
        )
        assert subtask.id == "sub-1"
        assert subtask.checked_datetime == datetime(
            2022, 12, 9, 16, 13, 52, tzinfo=timezone.utc
        )

    def test_minimum_subtask(self):
        subtask = Subtask(name="My sub-1")

        assert subtask.name == "My sub-1"
        assert subtask.is_checked is False

    def test_delete_themselves(self, requests_mock, client, task):
        requests_mock.delete(
            f"{API_BASE}/todo/lists/id-1/tasks/task-1/checklistItems/sub-1",
            status_code=204,
        )
        subtask = Subtask.from_dict(SUBTASK_EXAMPLE_DATA, client=client)
        subtask.task = task

        subtask.delete()

        assert requests_mock.called is True

    def test_create_raises_when_no_task(self):
        subtask = Subtask(name="Test")

        with pytest.raises(TaskNotSpecifiedError):
            subtask.create()

    def test_managing_endpoint_raises_when_no_tas(self):
        subtask = Subtask(name="Test")

        with pytest.raises(TaskNotSpecifiedError):
            subtask.managing_endpoint

    def test_raises_when_try_to_change_task(self, task):
        subtask = Subtask.from_dict(SUBTASK_EXAMPLE_DATA)
        subtask.task = task

        # Allow assign once more the same
        subtask.task = task

        task_2 = Task.from_dict({"id": "id-2"})
        with pytest.raises(UnsupportedOperationError):
            subtask.task = task_2

    def test_check_and_uncheck(self):
        subtask = Subtask(name="Test")

        subtask.check()

        assert subtask.is_checked is True
        assert isinstance(subtask.checked_datetime, datetime)

        subtask.uncheck()

        assert subtask.is_checked is False
        assert subtask.checked_datetime is None

    def test_deleting_removes_from_task(self, task, requests_mock):
        subtask = Subtask(name="aa", _id="test-1")

        task.add_subtask(subtask)

        assert len(task.subtasks) == 2
        assert subtask in task.subtasks

        requests_mock.delete(
            f"{API_BASE}/todo/lists/id-1/tasks/task-1/checklistItems/test-1",
            status_code=204,
        )

        subtask.delete()

        assert len(task.subtasks) == 1
        assert subtask not in task.subtasks

    def test_adding_subtask_to_empty_task(self, client):
        task = Task(title="test", client=client)

        task.add_subtask("Test 2")

        assert len(task.subtasks) == 1
