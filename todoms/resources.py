from abc import ABC
from datetime import datetime

from furl import furl

from .attributes import Importance, Status
from .convertable import BaseConvertableObject
from .converters.basic import (
    AttributeConverter,
    ContentAttrConverter,
    DatetimeAttrConverter,
    ImportanceAttrConverter,
    IsoTimeAttrConverter,
    StatusAttrConverter,
)
from .converters.recurrence import RecurrenceAttrConverter
from .filters import and_, ne


class ResourceAlreadyCreatedError(Exception):
    """This resource is already created. Prevent duplicate"""


class TaskListNotSpecifiedError(Exception):
    """TaskList id must be set before create task"""


class Resource(BaseConvertableObject, ABC):
    """Base Resource for any other"""

    ENDPOINT = ""
    ATTRIBUTES = ()

    def __init__(self, client):
        self._client = client

    def create(self):
        """Create object in API"""
        if self.id:
            raise ResourceAlreadyCreatedError
        result = self._client.raw_post(self.managing_endpoint, self.to_dict(), 201)
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
    def create_from_dict(cls, client, data_dict):
        return super().create_from_dict(data_dict, client=client)

    @classmethod
    def handle_list_filters(cls, *args, **kwargs):
        if len(args) + len(kwargs) == 0:
            return {}
        params = {"$filter": and_(*args, **kwargs)}
        return params


class TaskList(Resource):
    """Represent a list of tasks"""

    ENDPOINT = "todo/lists"
    ATTRIBUTES = (
        AttributeConverter("id", "_id"),
        AttributeConverter("displayName", "name"),
        AttributeConverter("isShared", "_is_shared"),
        AttributeConverter("isOwner", "_is_owner"),
        AttributeConverter("wellknownListName", "_well_known_name"),
    )

    def __init__(self, client, name: str):
        super().__init__(client)
        self.name = name

    def __repr__(self):
        return f"<TaskList '{self.name}'>"

    def __str__(self):
        return f"List '{self.name}'"

    def get_tasks(self, *args, **kwargs):
        """Get list of tasks in given list. Default returns only non-completed tasks."""
        tasks_endpoint = furl(self.ENDPOINT) / self.id / "tasks"
        return self._client.list(Task, endpoint=tasks_endpoint.url, *args, **kwargs)

    def save_task(self, task):
        task.task_list = self
        task.create()


class Task(Resource):
    """Represent a task."""

    ENDPOINT = "tasks"
    ATTRIBUTES = (
        AttributeConverter("id", "_id"),
        ContentAttrConverter("body", "body"),
        StatusAttrConverter("status", "status"),
        "title",
        RecurrenceAttrConverter("recurrence", "recurrence"),
        ImportanceAttrConverter("importance", "importance"),
        AttributeConverter("isReminderOn", "is_reminder_on"),
        IsoTimeAttrConverter("createdDateTime", "created_datetime"),
        DatetimeAttrConverter("dueDateTime", "due_datetime"),
        DatetimeAttrConverter("completedDateTime", "completed_datetime"),
        IsoTimeAttrConverter("lastModifiedDateTime", "last_modified_datetime"),
        DatetimeAttrConverter("reminderDateTime", "reminder_datetime"),
    )

    def __init__(
        self,
        client,
        title: str,
        body: str = None,
        status: Status = None,
        importance: Importance = None,
        recurrence: dict = None,
        is_reminder_on: bool = False,
        created_datetime: datetime = None,
        due_datetime: datetime = None,
        completed_datetime: datetime = None,
        last_modified_datetime: datetime = None,
        reminder_datetime: datetime = None,
        task_list: TaskList = None,
    ):
        super().__init__(client)
        self.body = body
        self.title = title
        self.status = status
        self.importance = importance
        self.recurrence = recurrence
        self.is_reminder_on = is_reminder_on
        self.created_datetime = created_datetime
        self.due_datetime = due_datetime
        self.completed_datetime = completed_datetime
        self.last_modified_datetime = last_modified_datetime
        self.reminder_datetime = reminder_datetime
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
        return (furl(self.task_list.managing_endpoint) / super().managing_endpoint).url
