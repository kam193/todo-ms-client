from datetime import datetime
from typing import TYPE_CHECKING, Any, Iterable, Optional, Type, TypeVar, Union

from furl import furl  # type: ignore

from todoms.converters.basic import ResourceConverter

from .attributes import Importance, Status
from .convertable import BaseConvertableFieldsObject, ConvertableType
from .fields.basic import (
    Attribute,
    Boolean,
    ContentField,
    Datetime,
    EnumField,
    IsoTime,
    List,
)
from .fields.recurrence import DueDatetime, RecurrenceField
from .filters import Comparable, and_, ne

if TYPE_CHECKING:
    from .client import ToDoClient


class ResourceAlreadyCreatedError(Exception):
    """This resource is already created. Prevent duplicate"""


class TaskListNotSpecifiedError(Exception):
    """TaskList id must be set before create task"""


class TaskNotSpecifiedError(Exception):
    """Task id must be set before creating subtask"""


class UnsupportedOperationError(Exception):
    """This operation is not supported"""


ResourceType = TypeVar("ResourceType", bound="Resource")


class Resource(BaseConvertableFieldsObject):
    """Base Resource for any other"""

    ENDPOINT = ""

    def __init__(
        self, *args: Any, client: Optional["ToDoClient"] = None, **kwargs: Any
    ):
        super().__init__(*args, **kwargs)
        self._client = client

    def create(self) -> None:
        """Create object in API"""
        if self.id:
            raise ResourceAlreadyCreatedError
        data_dict = {k: v for k, v in self.to_dict().items() if v is not None}
        result = self.client.raw_post(self.managing_endpoint, data_dict, 201)
        self._from_dict(result)

    def update(self) -> None:
        """Update resource in API"""
        response = self.client.patch(self)
        self._from_dict(response)

    def delete(self) -> None:
        """Delete object in API"""
        self.client.delete(self)

    @property
    def client(self) -> "ToDoClient":
        if not self._client:
            raise ValueError("Client not set")
        return self._client

    @client.setter
    def client(self, value: "ToDoClient") -> None:
        self._client = value

    @property
    def managing_endpoint(self) -> str:
        return str((furl(self.ENDPOINT) / (self.id or "")).url)

    @property
    def id(self) -> Optional[str]:
        return getattr(self, "_id", None)

    @classmethod
    def from_dict(  # type: ignore[override]
        cls: Type[ConvertableType],
        data_dict: dict,
        client: Optional["ToDoClient"] = None,
    ) -> ConvertableType:
        return super().from_dict(data_dict, client=client)

    def _clear(self) -> None:
        for field in self._fields:
            delattr(self, field.name)

    def refresh(self) -> None:
        new_data = self.client.raw_get(endpoint=self.managing_endpoint)
        self._clear()
        self._from_dict(new_data)

    @classmethod
    def handle_list_filters(cls, *args: str, **kwargs: Comparable) -> dict:
        not_empty_kwargs = {k: v for k, v in kwargs.items() if v is not None}
        if len(args) + len(not_empty_kwargs) == 0:
            return {}
        params = {"$filter": and_(*args, **not_empty_kwargs)}
        return params

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            raise NotImplementedError
        if not self.id or not other.id:
            return False
        return self.id == other.id


class TaskList(Resource):
    """Represent a list of tasks"""

    ENDPOINT = "todo/lists"
    _id = Attribute("id", read_only=True)
    name = Attribute("displayName")
    is_shared = Boolean("isShared", read_only=True, export=False)
    is_owner = Boolean("isOwner", read_only=True)
    well_known_name = Attribute("wellknownListName", read_only=True)

    def get_tasks(self, **kwargs: Any) -> Iterable["Task"]:
        """Iterate over tasks in the list. Default returns only non-completed tasks."""
        tasks_endpoint = furl(self.ENDPOINT) / self.id / Task.ENDPOINT
        tasks_gen = self.client.list(Task, endpoint=tasks_endpoint.url, **kwargs)
        for task in tasks_gen:
            task.task_list = self
            yield task

    @property
    def open_tasks(self) -> Iterable["Task"]:
        """Iterate over opened tasks"""
        return self.get_tasks(status=ne(Status.COMPLETED))

    @property
    def tasks(self) -> Iterable["Task"]:
        """Iterate over all tasks in this list"""
        return self.get_tasks(status=None)

    def save_task(self, task: "Task") -> None:
        task.task_list = self
        task.create()

    def __repr__(self) -> str:
        return f"<TaskList '{self.name}'>"

    def __str__(self) -> str:
        return f"List '{self.name}'"


class Subtask(Resource):
    """Represents a subtask element"""

    ENDPOINT = "checklistItems"

    _id = Attribute("id")
    created_datetime = IsoTime("createdDateTime", read_only=True, export=False)
    checked_datetime = IsoTime("checkedDateTime")
    name = Attribute("displayName")
    is_checked = Boolean("isChecked", default=False)

    def __init__(
        self,
        *args: Any,
        _task: Optional["Task"] = None,
        client: Optional["ToDoClient"] = None,
        **kwargs: Any,
    ):
        super().__init__(*args, client=client, **kwargs)
        self._task = _task

    @property
    def task(self) -> Optional["Task"]:
        return self._task

    @task.setter
    def task(self, value: "Task") -> None:
        if self._task and self._task.id != value.id:
            raise UnsupportedOperationError(
                "Moving subtask between tasks is not supported by the API"
            )
        self._task = value

    def create(self) -> None:
        if not self.task:
            raise TaskNotSpecifiedError
        return super().create()

    @property
    def managing_endpoint(self) -> str:
        if not self._task:
            raise TaskNotSpecifiedError
        return str((furl(self._task.managing_endpoint) / super().managing_endpoint).url)

    def check(self) -> None:
        self.is_checked = True
        self.checked_datetime = datetime.utcnow()

    def uncheck(self) -> None:
        self.is_checked = False
        self.checked_datetime = None

    def delete(self) -> None:
        super().delete()
        if self.task.subtasks and self in self.task.subtasks:  # type: ignore
            self.task.subtasks.remove(self)  # type: ignore

    def __repr__(self) -> str:
        return f"<Subtask '{self.name}'>"

    def __str__(self) -> str:
        return f"Subtask '{self.name}'"


def _post_subtask_convert(instance: "Task", subtasks: list[Subtask]) -> list[Subtask]:
    if subtasks:
        for subtask in subtasks:
            subtask.task = instance
            subtask.client = instance.client
    return subtasks


class Task(Resource):
    """Represent a task."""

    ENDPOINT = "tasks"

    _id = Attribute("id")
    body = ContentField("body")
    title = Attribute("title")
    status = EnumField("status", Status, default=Status.NOT_STARTED)
    importance = EnumField("importance", Importance, default=Importance.NORMAL)
    recurrence = RecurrenceField("recurrence")
    is_reminder_on = Boolean("isReminderOn", default=False)
    created_datetime = IsoTime("createdDateTime", read_only=True)
    due_datetime = DueDatetime("dueDateTime")
    completed_datetime = Datetime("completedDateTime", read_only=True)
    last_modified_datetime = IsoTime("lastModifiedDateTime", read_only=True)
    reminder_datetime = Datetime("reminderDateTime")
    categories = List("categories", Attribute)
    has_attachments = Boolean("hasAttachments", default=False, read_only=True)
    start_datetime = Datetime("startDateTime", read_only=True)
    subtasks = List(
        "checklistItems",
        ResourceConverter(Subtask),
        post_convert=_post_subtask_convert,
        export=False,
        default_factory=list,
    )

    def __init__(
        self,
        *args: Any,
        task_list: Optional[TaskList] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._task_list = task_list

    def _update_or_create_subtasks(self, subtasks: list[Subtask]) -> None:
        for subtask in subtasks:
            subtask.task = self
            subtask.client = self.client
            if not subtask.id:
                subtask.create()
            else:
                subtask.update()

    def create(self) -> None:
        if not self._task_list:
            raise TaskListNotSpecifiedError
        subtasks = self.subtasks
        super().create()
        self._update_or_create_subtasks(subtasks=subtasks)  # type: ignore

    def update(self) -> None:
        self._update_or_create_subtasks(subtasks=self.subtasks)  # type: ignore
        return super().update()

    @classmethod
    def handle_list_filters(cls, *args: str, **kwargs: Any) -> dict:
        kwargs.setdefault("status", ne(Status.COMPLETED))
        return super().handle_list_filters(*args, **kwargs)

    @property
    def managing_endpoint(self) -> str:
        if not self._task_list:
            raise TaskListNotSpecifiedError
        return str(
            (furl(self._task_list.managing_endpoint) / super().managing_endpoint).url
        )

    @property
    def task_list(self) -> Optional[TaskList]:
        return self._task_list

    @task_list.setter
    def task_list(self, value: TaskList) -> None:
        if self._task_list and self._task_list.id != value.id:
            raise UnsupportedOperationError(
                "Moving task between lists is not supported by the API"
            )
        self._task_list = value

    def save_subtask(self, subtask: Subtask) -> None:
        self.add_subtask(subtask)
        subtask.create()

    def add_subtask(self, subtask: Union[Subtask, str]) -> None:
        if isinstance(subtask, str):
            subtask = Subtask(name=subtask)
        subtask.task = self
        subtask.client = self.client
        if self.subtasks is None:
            self.subtasks = list()
        if subtask not in self.subtasks:  # type: ignore
            self.subtasks.append(subtask)  # type: ignore

    def __repr__(self) -> str:
        return f"<Task '{self.title}'>"

    def __str__(self) -> str:
        return f"Task '{self.title}'"
