from abc import ABC
from typing import TYPE_CHECKING, Optional, TypeVar

from furl import furl  # type: ignore

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
from .filters import and_, ne

if TYPE_CHECKING:
    from .client import ToDoClient


class ResourceAlreadyCreatedError(Exception):
    """This resource is already created. Prevent duplicate"""


class TaskListNotSpecifiedError(Exception):
    """TaskList id must be set before create task"""


class UnsupportedOperationError(Exception):
    """This operation is not supported"""


ResourceType = TypeVar("ResourceType", bound="Resource")


class Resource(BaseConvertableFieldsObject, ABC):
    """Base Resource for any other"""

    ENDPOINT = ""

    def __init__(self, client: Optional[ToDoClient] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._client = client

    def create(self) -> None:
        """Create object in API"""
        if self.id:
            raise ResourceAlreadyCreatedError
        data_dict = {k: v for k, v in self.to_dict().items() if v is not None}
        result = self._client.raw_post(self.managing_endpoint, data_dict, 201)
        self._from_dict(result)

    def update(self) -> None:
        """Update resource in API"""
        response = self._client.patch(self)
        self._from_dict(response)

    def delete(self) -> None:
        """Delete object in API"""
        self._client.delete(self)

    @property
    def managing_endpoint(self) -> str:
        return (furl(self.ENDPOINT) / (self.id or "")).url

    @property
    def id(self) -> Optional[str]:
        return getattr(self, "_id", None)

    @classmethod
    def from_dict(cls, client: ToDoClient, data_dict: dict) -> ConvertableType:
        return super().from_dict(data_dict, client=client)

    def _clear(self) -> None:
        for field in self._fields:
            delattr(self, field.name)

    def refresh(self) -> None:
        new_data = self._client.raw_get(endpoint=self.managing_endpoint)
        self._clear()
        self._from_dict(new_data)

    @classmethod
    def handle_list_filters(cls, *args, **kwargs) -> dict:
        not_empty_kwargs = {k: v for k, v in kwargs.items() if v is not None}
        if len(args) + len(not_empty_kwargs) == 0:
            return {}
        params = {"$filter": and_(*args, **not_empty_kwargs)}
        return params

    def __eq__(self, other: object) -> bool:
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

    def get_tasks(self, *args, **kwargs):
        """Iterate over tasks in the list. Default returns only non-completed tasks."""
        tasks_endpoint = furl(self.ENDPOINT) / self.id / "tasks"
        tasks_gen = self._client.list(
            Task, endpoint=tasks_endpoint.url, *args, **kwargs
        )
        for task in tasks_gen:
            task.task_list = self
            yield task

    @property
    def open_tasks(self):
        """Iterate over opened tasks"""
        return self.get_tasks(status=ne(Status.COMPLETED))

    @property
    def tasks(self):
        """Iterate over all tasks in this list"""
        return self.get_tasks(status=None)

    def save_task(self, task):
        task.task_list = self
        task.create()

    def __repr__(self):
        return f"<TaskList '{self.name}'>"

    def __str__(self):
        return f"List '{self.name}'"


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

    def __init__(
        self,
        *args,
        task_list: Optional[TaskList] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._task_list = task_list

    def create(self):
        if not self._task_list:
            raise TaskListNotSpecifiedError
        return super().create()

    @classmethod
    def handle_list_filters(cls, *args, **kwargs):
        kwargs.setdefault("status", ne(Status.COMPLETED))
        return super().handle_list_filters(*args, **kwargs)

    @property
    def managing_endpoint(self):
        if not self._task_list:
            raise TaskListNotSpecifiedError
        return (furl(self._task_list.managing_endpoint) / super().managing_endpoint).url

    @property
    def task_list(self):
        return self._task_list

    @task_list.setter
    def task_list(self, value: TaskList):
        if self._task_list and self._task_list.id != value.id:
            raise UnsupportedOperationError(
                "Moving task between lists is not supported by the API"
            )
        self._task_list = value

    def __repr__(self):
        return f"<Task '{self.title}'>"

    def __str__(self):
        return f"Task '{self.title}'"
