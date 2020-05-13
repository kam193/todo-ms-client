from todoms.resources import AttributeTranslator, Resource, TaskList

from .utils.constants import API_BASE

TASK_LIST_EXAMPLE_DATA = {
    "changeKey": "abc",
    "id": "id-1",
    "isDefaultFolder": True,
    "name": "list-name",
    "parentGroupKey": "group-1",
}


def test_default_resource_init_creates_obj_from_definition():
    class SimpleResource(Resource):
        ATTRIBUTES = ("id", "name")

    obj = SimpleResource(None, id="id-1", name="name-1", not_attr="ignore")

    assert obj.id == "id-1"
    assert obj.name == "name-1"
    assert getattr(obj, "not_attr", None) is None


def test_default_resource_init_translate_attributes():
    class ComplexResource(Resource):
        ATTRIBUTES = (AttributeTranslator("old", "new"),)

    obj_1 = ComplexResource(None, old="data")
    obj_2 = ComplexResource(None, new="data")

    assert obj_1.new == "data"
    assert obj_2.new == "data"


def test_create_tasklist_object_from_data():
    task_list = TaskList(None, **TASK_LIST_EXAMPLE_DATA)

    assert task_list.id == "id-1"
    assert task_list.name == "list-name"
    assert task_list.is_default is True
    assert task_list._change_key == "abc"
    assert task_list._parent_group_key == "group-1"


def test_list_tasklist_returns_proper_obj(client, requests_mock):
    requests_mock.get(
        f"{API_BASE}/outlook/taskFolders", json={"value": [{"id": "list-1"}]}
    )

    task_lists = client.list(TaskList)

    assert len(task_lists) == 1
    assert task_lists[0].id == "list-1"
