from abc import ABC
from datetime import datetime

from .converters import (
    AttributeConverter,
    ContentAttrConverter,
    DatetimeAttrConverter,
    IsoTimeAttrConverter,
)


class Resource(ABC):
    """Base Resource for any other"""

    ENDPOINT = ""
    ATTRIBUTES = ()

    def __init__(self, client):
        self._client = client

    def to_dict(self):
        data_dict = {}

        for attr in self.ATTRIBUTES:
            if isinstance(attr, AttributeConverter):
                value = getattr(self, attr.local_name)
                data_dict[attr.original_name] = attr.back_converter(value)
            else:
                data_dict[attr] = getattr(self, attr)

        return data_dict

    @classmethod
    def create_from_dict(cls, client, data_dict: dict):
        init_arguments = {}
        private_attributes = {}

        for attr in cls.ATTRIBUTES:
            if isinstance(attr, AttributeConverter):
                value = attr.obj_converter(data_dict.get(attr.original_name))
                if attr.local_name.startswith("_"):
                    private_attributes[attr.local_name] = value
                else:
                    init_arguments[attr.local_name] = value
            else:
                init_arguments[attr] = data_dict.get(attr)

        obj = cls(client, **init_arguments)
        for attr, value in private_attributes.items():
            setattr(obj, attr, value)

        return obj

    @classmethod
    def handle_list_filters(cls, **kwargs):
        return {}


class TaskList(Resource):
    """Represent a list of tasks"""

    ENDPOINT = "outlook/taskFolders"
    ATTRIBUTES = (
        "id",
        "name",
        AttributeConverter("isDefaultFolder", "is_default"),
        AttributeConverter("changeKey", "_change_key"),
        AttributeConverter("parentGroupKey", "_parent_group_key"),
    )

    def __init__(self, client, id: str, name: str, is_default: bool = False):
        super().__init__(client)
        self.id = id
        self.name = name
        self.is_default = is_default

    def get_tasks(self, status: str = "ne 'completed'"):
        tasks_endpoint = f"{self.ENDPOINT}/{self.id}/tasks"
        return self._client.list(Task, endpoint=tasks_endpoint, status=status)

    def delete(self):
        self._client.delete(self)

    def __repr__(self):
        return f"<TaskList '{self.name}'>"

    def __str__(self):
        return f"List '{self.name}'"


class Task(Resource):
    """Represent a task. Listing tasks without specific TaskList returns all tasks"""

    ENDPOINT = "outlook/tasks"
    ATTRIBUTES = (  # TODO: translate & format dates
        "id",
        ContentAttrConverter("body", "body"),
        "categories",
        "status",
        "subject",
        "sensitivity",
        "owner",
        "recurrence",
        "importance",
        AttributeConverter("assignedTo", "assigned_to"),
        AttributeConverter("hasAttachments", "has_attachments"),
        AttributeConverter("isReminderOn", "is_reminder_on"),
        AttributeConverter("parentFolderId", "task_list_id"),
        IsoTimeAttrConverter("createdDateTime", "created_datetime"),
        DatetimeAttrConverter("dueDateTime", "due_datetime"),
        DatetimeAttrConverter("startDateTime", "start_datetime"),
        DatetimeAttrConverter("completedDateTime", "completed_datetime"),
        IsoTimeAttrConverter("lastModifiedDateTime", "last_modified_datetime"),
        DatetimeAttrConverter("reminderDateTime", "reminder_datetime"),
        AttributeConverter("changeKey", "_change_key"),
    )

    def __init__(
        self,
        client,
        id: str,
        body: str,
        subject: str,
        task_list_id: str,
        status: str = None,
        importance: str = None,
        sensitivity: str = None,
        recurrence: dict = None,
        categories: list = None,
        owner: str = None,
        assigned_to: str = None,
        has_attachments: bool = False,
        is_reminder_on: bool = False,
        created_datetime: datetime = None,
        due_datetime: datetime = None,
        start_datetime: datetime = None,
        completed_datetime: datetime = None,
        last_modified_datetime: datetime = None,
        reminder_datetime: datetime = None,
    ):
        super().__init__(client)
        self.id = id
        self.body = body
        self.subject = subject
        self.task_list_id = task_list_id
        self.status = status
        self.importance = importance
        self.sensitivity = sensitivity
        self.recurrence = recurrence
        self.categories = categories
        self.owner = owner
        self.assigned_to = assigned_to
        self.has_attachments = has_attachments
        self.is_reminder_on = is_reminder_on
        self.created_datetime = created_datetime
        self.due_datetime = due_datetime
        self.start_datetime = start_datetime
        self.completed_datetime = completed_datetime
        self.last_modified_datetime = last_modified_datetime
        self.reminder_datetime = reminder_datetime

    def __repr__(self):
        return f"<Task '{self.subject}'>"

    def __str__(self):
        return f"Task '{self.subject}'"

    def delete(self):
        self._client.delete(self)

    @classmethod
    def handle_list_filters(cls, **kwargs):
        kwargs.setdefault("status", "ne 'completed'")
        params = {"$filter": f"status {kwargs['status']}" if kwargs["status"] else None}
        return params
