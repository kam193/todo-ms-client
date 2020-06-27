import copy
import urllib
from datetime import datetime, timezone

import pytest

from todoms.attributes import Importance, Sensitivity, Status
from todoms.filters import and_, eq
from todoms.resources import (
    Attachment,
    AttributeConverter,
    ContentAttrConverter,
    NotSupportedError,
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
    "importance": "high",
    "isReminderOn": True,
    "lastModifiedDateTime": "2021-01-01T18:00:00Z",
    "owner": "user-1",
    "parentFolderId": "id-1",
    "recurrence": {"@odata.type": "microsoft.graph.patternedRecurrence"},
    "reminderDateTime": {"dateTime": "2020-05-03T00:00:00.000000", "timeZone": "UTC"},
    "sensitivity": "normal",
    "startDateTime": {"dateTime": "2020-05-04T00:00:00.000000", "timeZone": "UTC"},
    "status": "notStarted",
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
    "resource,data",
    [
        (TaskList, TASK_LIST_EXAMPLE_DATA),
        (Task, TASK_EXAMPLE_DATA),
        (Attachment, ATTACHMENT_EXAMPLE_DATA),
    ],
)
def test_resource_is_proper_converted_back_to_dict(resource, data):
    obj = resource.create_from_dict(None, data)
    assert data == obj.to_dict()


class TestDefaultResource:
    def test_default_resource_init_creates_obj_from_data(self, simple_resource_class):
        obj = simple_resource_class.create_from_dict(
            None, {"_id": "id-1", "name": "name-1", "not_attr": "ignore"}
        )

        assert obj._id == "id-1"
        assert obj.name == "name-1"
        assert getattr(obj, "not_attr", None) is None

    def test_default_resource_init_translate_attributes(self):
        class ComplexResource(Resource):
            ATTRIBUTES = (AttributeConverter("old", "new"),)

            def __init__(self, client, new):
                super().__init__(client)
                self.new = new

        obj_1 = ComplexResource.create_from_dict(None, {"old": "data"})

        assert obj_1.new == "data"

    def test_default_resource_init_converts_attributes_format(self):
        class ComplexResource(Resource):
            ATTRIBUTES = (ContentAttrConverter("old", "new"),)

            def __init__(self, client, new):
                super().__init__(client)
                self.new = new

        obj_1 = ComplexResource.create_from_dict(
            None, {"old": {"content": "converted"}}
        )

        assert obj_1.new == "converted"

    def test_default_resource_simple_to_dict(self, simple_resource_class):
        resource = simple_resource_class.create_from_dict(
            None, {"_id": "id-1", "name": "name-1"}
        )

        resource_dict = resource.to_dict()

        assert resource_dict == {"_id": "id-1", "name": "name-1"}

    def test_default_resource_complex_to_dict(self):
        class ComplexResource(Resource):
            ATTRIBUTES = (AttributeConverter("old", "new"),)

            def __init__(self, client, new):
                super().__init__(client)
                self.new = new

        resource = ComplexResource(None, new="data")

        resource_dict = resource.to_dict()

        assert resource_dict == {"old": "data"}

    def test_default_resource_complex_to_dict_with_converter(self):
        class ComplexResource(Resource):
            ATTRIBUTES = (ContentAttrConverter("old", "new"),)

            def __init__(self, client, new):
                super().__init__(client)
                self.new = new

        resource = ComplexResource(None, new="data")

        resource_dict = resource.to_dict()

        assert resource_dict == {"old": {"content": "data", "contentType": "html"}}

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
            additional_matcher=match_body({"_id": None, "name": "new-resource"}),
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


class TestTaskListResource:
    def test_create_tasklist_object_from_data(self,):
        task_list = TaskList.create_from_dict(None, TASK_LIST_EXAMPLE_DATA)

        assert task_list.id == "id-1"
        assert task_list.name == "list-name"
        assert task_list.is_default is True
        assert task_list._change_key == "abc"
        assert task_list._parent_group_key == "group-1"

    def test_tasklist_get_tasks_returns_default_not_completed_tasks(
        self, client, requests_mock
    ):
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

    def test_task_list_delete_themselfs(self, requests_mock, client):
        requests_mock.delete(f"{API_BASE}/outlook/taskFolders/id-1", status_code=204)
        task_list = TaskList.create_from_dict(client, TASK_LIST_EXAMPLE_DATA)
        task_list.delete()
        assert requests_mock.called is True

    def test_task_list_saves_task(self, requests_mock, client):
        task_list = TaskList.create_from_dict(client, TASK_LIST_EXAMPLE_DATA)
        new_task = Task(client, "Test")

        expected_body = new_task.to_dict()
        expected_body["parentFolderId"] = "id-1"
        requests_mock.post(
            f"{API_BASE}/outlook/tasks",
            status_code=201,
            json={"id": "new_id"},
            additional_matcher=match_body(expected_body),
        )

        task_list.save_task(new_task)

        assert new_task.task_list_id == "id-1"
        assert new_task.id == "new_id"
        assert requests_mock.called is True


class TestTaskResource:
    def test_default_crucial_values(self):
        task = Task(None, "Subject")

        assert task.id is None
        assert task.categories == []
        assert task.subject == "Subject"

    def test_create_task_object_from_dict(self):
        task = Task.create_from_dict(None, TASK_EXAMPLE_DATA)

        assert task.id == "task-1"
        assert task.body == "task-body"
        assert task.categories == ["category1"]
        assert task.status == Status.NOT_STARTED
        assert task.subject == "My new task"
        assert task.sensitivity == Sensitivity.NORMAL
        assert task.owner == "user-1"
        assert task.importance == Importance.HIGH
        assert task.assigned_to == "user-1"
        assert task.has_attachments is True
        assert task.is_reminder_on is True
        assert task.task_list_id == "id-1"
        assert task._change_key == "key-change-1"
        assert task.last_modified_datetime == datetime(
            2021, 1, 1, 18, tzinfo=timezone.utc
        )
        assert task.created_datetime == datetime(2020, 1, 1, 18, tzinfo=timezone.utc)
        assert task.completed_datetime == datetime(2020, 5, 1, tzinfo=timezone.utc)
        assert task.due_datetime == datetime(2020, 5, 2, tzinfo=timezone.utc)
        assert task.reminder_datetime == datetime(2020, 5, 3, tzinfo=timezone.utc)
        assert task.start_datetime == datetime(2020, 5, 4, tzinfo=timezone.utc)

    def test_task_handle_filters_default_completed(self):
        filters = Task.handle_list_filters()
        assert filters == {"$filter": "status ne 'completed'"}

    def test_task_handle_filters_select_status(self):
        filters = Task.handle_list_filters(status="my-filter")
        assert filters == {"$filter": "status my-filter"}

    def test_task_delete_themselfs(self, requests_mock, client):
        requests_mock.delete(f"{API_BASE}/outlook/tasks/task-1", status_code=204)
        task = Task.create_from_dict(client, TASK_EXAMPLE_DATA)
        task.delete()
        assert requests_mock.called is True

    def test_task_complete(self, requests_mock, client):
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
        assert task.status == Status.COMPLETED
        assert task.completed_datetime == datetime(2020, 6, 12, tzinfo=timezone.utc)

    def test_task_list_attachment(self, requests_mock, client):
        requests_mock.get(
            f"{API_BASE}/outlook/tasks/task-1/attachments",
            status_code=200,
            json={"value": [ATTACHMENT_EXAMPLE_DATA]},
        )
        task = Task.create_from_dict(client, TASK_EXAMPLE_DATA)

        result = task.list_attachments()

        assert len(result) == 1
        assert isinstance(result[0], Attachment) is True
        assert result[0].id == "attachment-1"
        assert result[0].task == task

    def test_task_create_raises_when_no_tasklist_id(self):
        task = Task(None, "Test")

        with pytest.raises(TaskListNotSpecifiedError):
            task.create()


class TestAttachmentResource:
    def test_attachment_from_dict(self):
        task = Task.create_from_dict(None, TASK_EXAMPLE_DATA)
        attachment = Attachment.create_from_dict(
            None, ATTACHMENT_EXAMPLE_DATA, task=task
        )

        assert attachment.task == task
        assert attachment.id == "attachment-1"
        assert attachment.is_inline is True
        assert attachment.content_type == "mime/type"
        assert attachment.last_modified_datetime == datetime(
            2021, 1, 1, 18, tzinfo=timezone.utc
        )
        assert attachment.name == "The Attachment"
        assert attachment.size == 1024

    def test_attachment_update_not_supported(self):
        attachment = Attachment.create_from_dict(
            None, ATTACHMENT_EXAMPLE_DATA, task=None
        )

        with pytest.raises(NotSupportedError):
            attachment.update()

    def test_attachment_managing_url(self):
        task = Task.create_from_dict(None, TASK_EXAMPLE_DATA)
        attachment = Attachment.create_from_dict(
            None, ATTACHMENT_EXAMPLE_DATA, task=task
        )

        assert (
            attachment.managing_endpoint
            == "outlook/tasks/task-1/attachments/attachment-1"
        )
