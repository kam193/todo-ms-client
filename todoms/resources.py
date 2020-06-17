from abc import ABC
from datetime import datetime

from furl import furl

from .converters import (
    AttributeConverter,
    ContentAttrConverter,
    DatetimeAttrConverter,
    IsoTimeAttrConverter,
)


class ResourceAlreadyCreatedError(Exception):
    """This resource is already created. Prevent duplicate"""


class NotSupportedError(Exception):
    """This method isn't supported in this resource type"""


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
                value = getattr(self, attr.local_name, None)
                data_dict[attr.original_name] = attr.back_converter(value)
            else:
                data_dict[attr] = getattr(self, attr, None)

        return data_dict

    def update(self):
        self._client.patch(self)

    def create(self):
        if self.id:
            raise ResourceAlreadyCreatedError
        result = self._client.raw_post(self.ENDPOINT, self.to_dict(), 201)
        # TODO: update object from result
        self._id = result.get("id", None)

    @property
    def id(self):
        return getattr(self, "_id", None)

    @classmethod
    def create_from_dict(cls, client, data_dict: dict):
        init_arguments = {}
        private_attributes = {}

        def store_attribute(name, value):
            if name.startswith("_"):
                private_attributes[name] = value
            else:
                init_arguments[name] = value

        for attr in cls.ATTRIBUTES:
            if isinstance(attr, AttributeConverter):
                value = attr.obj_converter(data_dict.get(attr.original_name))
                store_attribute(attr.local_name, value)
            else:
                store_attribute(attr, data_dict.get(attr))

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
        AttributeConverter("id", "_id"),
        "name",
        AttributeConverter("isDefaultFolder", "is_default"),
        AttributeConverter("changeKey", "_change_key"),
        AttributeConverter("parentGroupKey", "_parent_group_key"),
    )

    def __init__(self, client, name: str, is_default: bool = False):
        super().__init__(client)
        self.name = name
        self.is_default = is_default

    def get_tasks(self, status: str = "ne 'completed'"):
        tasks_endpoint = furl(self.ENDPOINT) / self.id / "tasks"
        return self._client.list(Task, endpoint=tasks_endpoint.url, status=status)

    def delete(self):
        self._client.delete(self)

    def __repr__(self):
        return f"<TaskList '{self.name}'>"

    def __str__(self):
        return f"List '{self.name}'"


class Task(Resource):
    """Represent a task. Listing tasks without specific TaskList returns all tasks"""

    ENDPOINT = "outlook/tasks"
    ATTRIBUTES = (
        AttributeConverter("id", "_id"),
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

    def complete(self):
        endpoint = furl(self.ENDPOINT) / self.id / "complete"
        result = self._client.raw_post(endpoint.url, data={}, expected_code=200)

        # TODO: better update object from result
        self.status = result["value"][0]["status"]
        self.completed_datetime = DatetimeAttrConverter("", "").obj_converter(
            result["value"][0]["completedDateTime"]
        )

    def list_attachments(self):
        endpoint = furl(self.ENDPOINT) / self.id / Attachment.ENDPOINT
        attachments = self._client.list(Attachment, endpoint.url)

        for attachment in attachments:
            attachment.task = self

        return attachments

    @classmethod
    def handle_list_filters(cls, **kwargs):
        kwargs.setdefault("status", "ne 'completed'")
        params = {"$filter": f"status {kwargs['status']}" if kwargs["status"] else None}
        return params


class Attachment(Resource):
    """Represent a generic attachment attachted to a task"""

    ENDPOINT = "attachments"
    ATTRIBUTES = (
        AttributeConverter("id", "_id"),
        "name",
        "size",
        AttributeConverter("isInline", "is_inline"),
        AttributeConverter("contentType", "content_type"),
        IsoTimeAttrConverter("lastModifiedDateTime", "last_modified_datetime"),
    )

    def __repr__(self):
        return f"<Attachment '{self.name}'>"

    def __str__(self):
        return f"Attachment '{self.name}'"

    def __init__(
        self,
        client,
        name: str,
        size: int,
        content_type: str,
        is_inline: bool = True,
        last_modified_datetime: datetime = None,
        task: Task = None,
    ):
        super().__init__(client)
        self.task = task
        self.name = name
        self.size = size
        self.content_type = content_type
        self.is_inline = is_inline
        self.last_modified_datetime = last_modified_datetime

    def update(self):
        raise NotSupportedError

    @classmethod
    def create_from_dict(cls, client, data_dict, task=None):
        attachment = super().create_from_dict(client, data_dict)
        attachment.task = task
        return attachment
