from abc import ABC

from furl import furl

from .attributes import Status
from .convertable import BaseConvertableFieldsObject
from .fields.basic import (
    Attribute,
    Content,
    Datetime,
    ImportanceField,
    IsoTime,
    StatusField,
)
from .fields.recurrence import RecurrenceField
from .filters import and_, ne


class ResourceAlreadyCreatedError(Exception):
    """This resource is already created. Prevent duplicate"""


class TaskListNotSpecifiedError(Exception):
    """TaskList id must be set before create task"""


class Resource(BaseConvertableFieldsObject, ABC):
    """Base Resource for any other"""

    ENDPOINT = ""

    def __init__(self, client, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._client = client

    def create(self):
        """Create object in API"""
        if self.id:
            raise ResourceAlreadyCreatedError
        data_dict = {k: v for k, v in self.to_dict().items() if v is not None}
        result = self._client.raw_post(self.managing_endpoint, data_dict, 201)
        # TODO: update object from result
        self._id = result.get("id", None)

    def update(self):
        """Update resource in API"""
        self._client.patch(self)

    def delete(self):
        """Delete object in API"""
        self._client.delete(self)

    @property
    def managing_endpoint(self):
        return (furl(self.ENDPOINT) / (self.id or "")).url

    @property
    def id(self):
        return getattr(self, "_id", None)

    @classmethod
    def from_dict(cls, client, data_dict):
        return super().from_dict(data_dict, client=client)

    @classmethod
    def handle_list_filters(cls, *args, **kwargs):
        not_empty_kwargs = {k: v for k, v in kwargs.items() if v is not None}
        if len(args) + len(not_empty_kwargs) == 0:
            return {}
        params = {"$filter": and_(*args, **not_empty_kwargs)}
        return params


class TaskList(Resource):
    """Represent a list of tasks"""

    ENDPOINT = "todo/lists"
    _id = Attribute("id")
    name = Attribute("displayName")
    _is_shared = Attribute("isShared")
    _is_owner = Attribute("isOwner")
    _well_known_name = Attribute("wellknownListName")

    def __repr__(self):
        return f"<TaskList '{self.name}'>"

    def __str__(self):
        return f"List '{self.name}'"

    def get_tasks(self, *args, **kwargs):
        """Get list of tasks in given list. Default returns only non-completed tasks."""
        tasks_endpoint = furl(self.ENDPOINT) / self.id / "tasks"
        tasks = self._client.list(Task, endpoint=tasks_endpoint.url, *args, **kwargs)
        for task in tasks:
            task.task_list = self
        return tasks

    def save_task(self, task):
        task.task_list = self
        task.create()


class Task(Resource):
    """Represent a task."""

    ENDPOINT = "tasks"

    _id = Attribute("id")
    body = Content("body")
    title = Attribute("title")
    status = StatusField("status")
    importance = ImportanceField("importance")
    recurrence = RecurrenceField("recurrence")
    is_reminder_on = Attribute("isReminderOn")
    created_datetime = IsoTime("createdDateTime")
    due_datetime = Datetime("dueDateTime")
    completed_datetime = Datetime("completedDateTime")
    last_modified_datetime = IsoTime("lastModifiedDateTime")
    reminder_datetime = Datetime("reminderDateTime")

    def __init__(
        self, *args, task_list: TaskList = None, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.task_list = task_list

    def __repr__(self):
        return f"<Task '{self.title}'>"

    def __str__(self):
        return f"Task '{self.title}'"

    def create(self):
        if not self.task_list:
            raise TaskListNotSpecifiedError
        return super().create()

    @classmethod
    def handle_list_filters(cls, *args, **kwargs):
        kwargs.setdefault("status", ne(Status.COMPLETED))
        return super().handle_list_filters(*args, **kwargs)

    @property
    def managing_endpoint(self):
        if not self.task_list:
            raise TaskListNotSpecifiedError
        return (furl(self.task_list.managing_endpoint) / super().managing_endpoint).url
