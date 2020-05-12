from todoms.resources import TaskList

from .utils.constants import API_BASE

TASK_LIST_EXAMPLE = {
    "changeKey": "abc",
    "id": "id-1",
    "isDefaultFolder": True,
    "name": "list-name",
    "parentGroupKey": "group-1",
}


def test_create_task_list_object():
    task_list = TaskList(None, **TASK_LIST_EXAMPLE)

    assert task_list.id == "id-1"
    assert task_list.name == "list-name"
    assert task_list.is_default is True
    assert task_list._change_key == "abc"
    assert task_list._parent_group_key == "group-1"


def test_list_task_list_returns_proper_obj(client, requests_mock):
    requests_mock.get(
        f"{API_BASE}/outlook/taskFolders", json={"value": [{"id": "list-1"}]}
    )

    task_lists = client.list(TaskList)

    assert len(task_lists) == 1
    assert task_lists[0].id == "list-1"
