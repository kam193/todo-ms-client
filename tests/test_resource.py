import copy
import urllib
from datetime import datetime, timezone

import pytest

from todoms.resources import (
    AttributeConverter,
    ContentAttrConverter,
    Resource,
    ResourceAlreadyCreatedError,
    Task,
    TaskList,
    Attachment,
    NotSupportedError,
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
    "completedDateTime": {"dateTime": "2020-05-01T00:00:00.000000", "timeZone": "UTC"},
    "createdDateTime": "2020-01-01T18:00:00Z",
    "dueDateTime": {"dateTime": "2020-05-02T00:00:00.000000", "timeZone": "UTC"},
    "hasAttachments": True,
    "id": "task-1",
    "importance": "urgent",
    "isReminderOn": True,
    "lastModifiedDateTime": "2021-01-01T18:00:00Z",
    "owner": "user-1",
    "parentFolderId": "id-1",
    "recurrence": {"@odata.type": "microsoft.graph.patternedRecurrence"},
    "reminderDateTime": {"dateTime": "2020-05-03T00:00:00.000000", "timeZone": "UTC"},
    "sensitivity": "top-secret",
    "startDateTime": {"dateTime": "2020-05-04T00:00:00.000000", "timeZone": "UTC"},
    "status": "status-1",
    "subject": "My new task",
}

ATTACHMENT_EXAMPLE_DATA = {
    "contentType": "mime/type",
    "id": "attachment-1",
    "isInline": True,
    "lastModifiedDateTime": "2021-01-01T18:00:00Z",
    "name": "The Attachment",
    "size": 1024,
}


def test_default_resource_init_creates_obj_from_data(simple_resource_class):
    obj = simple_resource_class.create_from_dict(
        None, {"_id": "id-1", "name": "name-1", "not_attr": "ignore"}
    )

    assert obj._id == "id-1"
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
        ATTRIBUTES = (ContentAttrConverter("old", "new"),)

        def __init__(self, client, new):
            super().__init__(client)
            self.new = new

    obj_1 = ComplexResource.create_from_dict(None, {"old": {"content": "converted"}})

    assert obj_1.new == "converted"


def test_default_resource_simple_to_dict(simple_resource_class):
    resource = simple_resource_class.create_from_dict(
        None, {"_id": "id-1", "name": "name-1"}
    )

    resource_dict = resource.to_dict()

    assert resource_dict == {"_id": "id-1", "name": "name-1"}


def test_default_resource_complex_to_dict():
    class ComplexResource(Resource):
        ATTRIBUTES = (AttributeConverter("old", "new"),)

        def __init__(self, client, new):
            super().__init__(client)
            self.new = new

    resource = ComplexResource(None, new="data")

    resource_dict = resource.to_dict()

    assert resource_dict == {"old": "data"}


def test_default_resource_complex_to_dict_with_converter():
    class ComplexResource(Resource):
        ATTRIBUTES = (ContentAttrConverter("old", "new"),)

        def __init__(self, client, new):
            super().__init__(client)
            self.new = new

    resource = ComplexResource(None, new="data")

    resource_dict = resource.to_dict()

    assert resource_dict == {"old": {"content": "data", "contentType": "html"}}


def test_default_resource_update_client_call(client, requests_mock):
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


def test_default_resource_id(simple_resource_class):
    resource = simple_resource_class.create_from_dict(
        None, {"_id": "id-1", "name": "name-1"}
    )

    assert resource.id == "id-1"


def test_default_resource_id_return_none_when_unset(simple_resource_class):
    resource = simple_resource_class.create_from_dict(None, {"name": "name-1"})

    assert resource.id is None


def test_default_resource_create_fails_when_id_set(simple_resource_class):
    resource = simple_resource_class.create_from_dict(
        None, {"_id": "id-1", "name": "name-1"}
    )

    with pytest.raises(ResourceAlreadyCreatedError):
        resource.create()


def test_default_resource_create_calls_endpoint(
    simple_resource_class, client, requests_mock
):
    resource = simple_resource_class(client, name="new-resource")
    requests_mock.post(
        f"{API_BASE}/endpoint",
        json={"id": "new-id", "name": "new-resource"},
        status_code=201,
        additional_matcher=match_body({"_id": None, "name": "new-resource"}),
    )

    resource.create()

    assert requests_mock.called is True
    assert resource.id == "new-id"


@pytest.mark.parametrize(
    "resource,endpoint",
    [
        (TaskList, "outlook/taskFolders"),
        (Task, "outlook/tasks"),
        (Attachment, "attachments"),
    ],
)
def test_resource_has_proper_endpoint(resource, endpoint):
    assert resource.ENDPOINT == endpoint


@pytest.mark.parametrize(
    "resource,data", [(TaskList, TASK_LIST_EXAMPLE_DATA), (Task, TASK_EXAMPLE_DATA)]
)
def test_resource_is_proper_converted_back_to_dict(resource, data):
    obj = resource.create_from_dict(None, data)
    assert data == obj.to_dict()


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
    assert requests_mock.called is True


def test_task_list_delete_themselfs(requests_mock, client):
    requests_mock.delete(f"{API_BASE}/outlook/taskFolders/id-1", status_code=204)
    task_list = TaskList.create_from_dict(client, TASK_LIST_EXAMPLE_DATA)
    task_list.delete()
    assert requests_mock.called is True


def test_task_complete(requests_mock, client):
    response = copy.deepcopy(TASK_EXAMPLE_DATA)
    response["status"] = "completed"
    response["completedDateTime"] = {
        "dateTime": "2020-06-12T00:00:00.000000",
        "timeZone": "UTC",
    }

    requests_mock.post(
        f"{API_BASE}/outlook/tasks/task-1/complete",
        status_code=200,
        json={"value": [response]},
        additional_matcher=match_body({}),
    )
    task = Task.create_from_dict(client, TASK_EXAMPLE_DATA)
    task.complete()

    assert requests_mock.called is True
    assert task.status == "completed"
    assert task.completed_datetime == datetime(2020, 6, 12, tzinfo=timezone.utc)


def test_attachment_from_dict():
    task = Task.create_from_dict(None, TASK_EXAMPLE_DATA)
    attachment = Attachment.create_from_dict(None, task, ATTACHMENT_EXAMPLE_DATA)

    assert attachment.task == task
    assert attachment.id == "attachment-1"
    assert attachment.is_inline is True
    assert attachment.content_type == "mime/type"
    assert attachment.last_modified_datetime == datetime(
        2021, 1, 1, 18, tzinfo=timezone.utc
    )
    assert attachment.name == "The Attachment"
    assert attachment.size == 1024


def test_attachment_update_not_supported():
    attachment = Attachment.create_from_dict(None, None, ATTACHMENT_EXAMPLE_DATA)

    with pytest.raises(NotSupportedError):
        attachment.update()


def test_attachment_list_filter_not_supported():
    with pytest.raises(NotSupportedError):
        Attachment.handle_list_filters()
