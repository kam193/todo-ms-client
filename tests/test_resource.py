import urllib

from pytest import mark

from todoms.resources import AttributeTranslator, Resource, Task, TaskList

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
    "body": "task-body",
    "categories": ["category1"],
    "changeKey": "key-change-1",
    "completedDateTime": {"@odata.type": "microsoft.graph.dateTimeTimeZone"},
    "createdDateTime": "timestamp",
    "dueDateTime": {"@odata.type": "microsoft.graph.dateTimeTimeZone"},
    "hasAttachments": True,
    "id": "task-1",
    "importance": "urgent",
    "isReminderOn": True,
    "lastModifiedDateTime": "timestamp",
    "owner": "user-1",
    "parentFolderId": "id-1",
    "recurrence": {"@odata.type": "microsoft.graph.patternedRecurrence"},
    "reminderDateTime": {"@odata.type": "microsoft.graph.dateTimeTimeZone"},
    "sensitivity": "top-secret",
    "startDateTime": {"@odata.type": "microsoft.graph.dateTimeTimeZone"},
    "status": "status-1",
    "subject": "My new task",
}


def test_default_resource_init_creates_obj_from_data():
    class SimpleResource(Resource):
        ATTRIBUTES = ("id", "name")

    obj = SimpleResource.create(None, id="id-1", name="name-1", not_attr="ignore")

    assert obj.id == "id-1"
    assert obj.name == "name-1"
    assert getattr(obj, "not_attr", None) is None


def test_default_resource_init_translate_attributes():
    class ComplexResource(Resource):
        ATTRIBUTES = (AttributeTranslator("old", "new"),)

    obj_1 = ComplexResource.create(None, old="data")
    obj_2 = ComplexResource.create(None, new="data")

    assert obj_1.new == "data"
    assert obj_2.new == "data"


@mark.parametrize(
    "resource,endpoint", [(TaskList, "outlook/taskFolders"), (Task, "outlook/tasks")]
)
def test_resource_has_proper_endpoint(resource, endpoint):
    assert resource.ENDPOINT == endpoint


def test_create_tasklist_object_from_data():
    task_list = TaskList.create(None, **TASK_LIST_EXAMPLE_DATA)

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
    task_list = TaskList.create(client, **TASK_LIST_EXAMPLE_DATA)
    tasks = task_list.get_tasks()

    assert len(tasks) == 1
    assert tasks[0].id == "task-1"


def test_create_task_object_from_data():
    task = Task.create(None, **TASK_EXAMPLE_DATA)

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


def test_task_handle_filters_default_completed():
    filters = Task.handle_list_filters()
    assert filters == {"$filter": "status ne 'completed'"}


def test_task_handle_filters_select_status():
    filters = Task.handle_list_filters(status="my-filter")
    assert filters == {"$filter": "status my-filter"}
