import urllib
from datetime import datetime, timezone

from pytest import mark

from todoms.resources import AttributeConverter, Resource, Task, TaskList

from .utils.constants import API_BASE

TASK_LIST_EXAMPLE_DATA = {
    "changeKey": "abc",
    "id": "id-1",
    "isDefaultFolder": True,
    "name": "list-name",
    "parentGroupKey": "group-1",
}

TASK_EXAMPLE_DATA = {
    "assignedTo": "user-1",
    "body": {"content": "task-body", "contentType": "html"},
    "categories": ["category1"],
    "changeKey": "key-change-1",
    "completedDateTime": {"dateTime": "2020-05-01T00:00:00.0000000", "timeZone": "UTC"},
    "createdDateTime": "2020-01-01T18:00:00Z",
    "dueDateTime": {"dateTime": "2020-05-02T00:00:00.0000000", "timeZone": "UTC"},
    "hasAttachments": True,
    "id": "task-1",
    "importance": "urgent",
    "isReminderOn": True,
    "lastModifiedDateTime": "2021-01-01T18:00:00Z",
    "owner": "user-1",
    "parentFolderId": "id-1",
    "recurrence": {"@odata.type": "microsoft.graph.patternedRecurrence"},
    "reminderDateTime": {"dateTime": "2020-05-03T00:00:00.0000000", "timeZone": "UTC"},
    "sensitivity": "top-secret",
    "startDateTime": {"dateTime": "2020-05-04T00:00:00.0000000", "timeZone": "UTC"},
    "status": "status-1",
    "subject": "My new task",
}


def test_default_resource_init_creates_obj_from_data():
    class SimpleResource(Resource):
        ATTRIBUTES = ("id", "name")

        def __init__(self, client, id, name):
            super().__init__(client)
            self.id = id
            self.name = name

    obj = SimpleResource.create_from_dict(
        None, {"id": "id-1", "name": "name-1", "not_attr": "ignore"}
    )

    assert obj.id == "id-1"
    assert obj.name == "name-1"
    assert getattr(obj, "not_attr", None) is None


def test_default_resource_init_translate_attributes():
    class ComplexResource(Resource):
        ATTRIBUTES = (AttributeConverter("old", "new"),)

        def __init__(self, client, new):
            super().__init__(client)
            self.new = new

    obj_1 = ComplexResource.create_from_dict(None, {"old": "data"})

    assert obj_1.new == "data"


def test_default_resource_init_converts_attributes_format():
    class ComplexResource(Resource):
        ATTRIBUTES = (AttributeConverter("old", "new", lambda x: "converted"),)

        def __init__(self, client, new):
            super().__init__(client)
            self.new = new

    obj_1 = ComplexResource.create_from_dict(None, {"old": "data"})

    assert obj_1.new == "converted"


@mark.parametrize(
    "resource,endpoint", [(TaskList, "outlook/taskFolders"), (Task, "outlook/tasks")]
)
def test_resource_has_proper_endpoint(resource, endpoint):
    assert resource.ENDPOINT == endpoint


def test_create_tasklist_object_from_data():
    task_list = TaskList.create_from_dict(None, TASK_LIST_EXAMPLE_DATA)

    assert task_list.id == "id-1"
    assert task_list.name == "list-name"
    assert task_list.is_default is True
    assert task_list._change_key == "abc"
    assert task_list._parent_group_key == "group-1"


def test_tasklist_get_tasks_returns_default_not_completed_tasks(client, requests_mock):
    qs = urllib.parse.urlencode({"$filter": "status ne 'completed'"})
    requests_mock.get(
        f"{API_BASE}/outlook/taskFolders/id-1/tasks?{qs}",
        json={"value": [TASK_EXAMPLE_DATA]},
        complete_qs=True,
    )
    task_list = TaskList.create_from_dict(client, TASK_LIST_EXAMPLE_DATA)
    tasks = task_list.get_tasks()

    assert len(tasks) == 1
    assert tasks[0].id == "task-1"


def test_create_task_object_from_dict():
    task = Task.create_from_dict(None, TASK_EXAMPLE_DATA)

    assert task.id == "task-1"
    assert task.body == "task-body"
    assert task.categories == ["category1"]
    assert task.status == "status-1"
    assert task.subject == "My new task"
    assert task.sensitivity == "top-secret"
    assert task.owner == "user-1"
    assert task.importance == "urgent"
    assert task.assigned_to == "user-1"
    assert task.has_attachments is True
    assert task.is_reminder_on is True
    assert task.task_list_id == "id-1"
    assert task._change_key == "key-change-1"
    assert task.last_modified_datetime == datetime(2021, 1, 1, 18, tzinfo=timezone.utc)
    assert task.created_datetime == datetime(2020, 1, 1, 18, tzinfo=timezone.utc)
    assert task.completed_datetime == datetime(2020, 5, 1, tzinfo=timezone.utc)
    assert task.due_datetime == datetime(2020, 5, 2, tzinfo=timezone.utc)
    assert task.reminder_datetime == datetime(2020, 5, 3, tzinfo=timezone.utc)
    assert task.start_datetime == datetime(2020, 5, 4, tzinfo=timezone.utc)


def test_task_handle_filters_default_completed():
    filters = Task.handle_list_filters()
    assert filters == {"$filter": "status ne 'completed'"}


def test_task_handle_filters_select_status():
    filters = Task.handle_list_filters(status="my-filter")
    assert filters == {"$filter": "status my-filter"}


def test_task_delete_themselfs(requests_mock, client):
    requests_mock.delete(f"{API_BASE}/outlook/tasks/task-1", status_code=204)
    task = Task.create_from_dict(client, TASK_EXAMPLE_DATA)
    task.delete()


def test_task_list_delete_themselfs(requests_mock, client):
    requests_mock.delete(f"{API_BASE}/outlook/taskFolders/id-1", status_code=204)
    task_list = TaskList.create_from_dict(client, TASK_LIST_EXAMPLE_DATA)
    task_list.delete()
