import pytest

from todoms.client import ResourceNotFoundError
from todoms.resources import Task, TaskList

from ..test_resource import TASK_EXAMPLE_DATA, TASK_LIST_EXAMPLE_DATA
from .utils import run_functional_condition

pytestmark = run_functional_condition


@pytest.fixture
def task_list_data(generate_id):
    data = {
        **TASK_LIST_EXAMPLE_DATA,
        "displayName": generate_id("list"),
    }
    del data["id"]
    return data


@pytest.fixture
def task_data(generate_id):
    data = {
        **TASK_EXAMPLE_DATA,
        "title": generate_id("task"),
    }
    del data["id"]
    del data["recurrence"]  # TODO: Get back when #104 is implemented
    return data


@pytest.fixture
def task(client, task_list, task_data, clean_up):
    task = Task.from_dict(client, task_data)
    task_list.save_task(task)
    clean_up(task)
    return task


@pytest.fixture
def task_list(client, task_list_data, clean_up):
    task_list = TaskList.from_dict(client, task_list_data)
    task_list.create()
    clean_up(task_list)
    return task_list


def test_creating_task_list(client, task_list_data, clean_up):
    task_list = TaskList.from_dict(client, task_list_data)

    task_list.create()
    clean_up(task_list)
    assert task_list.id is not None

    downloaded_task_list = client.get(TaskList, task_list.id)
    assert downloaded_task_list is not None


def test_updating_task_list(client, task_list):
    task_list.name = "New name"
    task_list.update()

    downloaded_task_list = client.get(TaskList, task_list.id)
    assert downloaded_task_list.name == "New name"


def test_refreshing_task_and_task_list(client, task, task_list):
    old_title = task.title
    task.title = "New title"
    old_name = task_list.name
    task_list.name = "New name"

    task.refresh()
    task_list.refresh()

    assert task.title == old_title
    assert task_list.name == old_name


def test_deleting_task_list(client, task_list):
    task_list.delete()

    with pytest.raises(ResourceNotFoundError):
        client.get(TaskList, task_list.id)


def test_listing_task_lists(client, task_list):
    task_lists = client.list(TaskList)
    assert task_list.name in [t.name for t in task_lists]


def test_creating_task(client, task_list, task_data, clean_up):
    task = Task.from_dict(client, task_data)
    task_list.save_task(task)
    clean_up(task)

    tasks = task_list.get_tasks()
    task = next(t for t in tasks if t.title == task_data["title"])
    assert task.created_datetime is not None


def test_updating_task(client, task, task_list, run_id):
    task.title = f"New title-{run_id}"
    task.update()

    tasks = task_list.get_tasks()
    assert f"New title-{run_id}" in [t.title for t in tasks]


def test_deleting_task(client, task, task_list):
    task.delete()

    tasks = task_list.get_tasks()
    assert task.title not in [t.title for t in tasks]
