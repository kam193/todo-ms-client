from abc import ABC
from dataclasses import dataclass


@dataclass
class AttributeTranslator:
    original_name: str
    local_name: str


class Resource(ABC):
    """Base Resource for any other"""

    ENDPOINT = ""
    ATTRIBUTES = ()

    def __init__(self, client, **kwargs):
        self._client = client
        for attr in self.ATTRIBUTES:
            if isinstance(attr, AttributeTranslator):
                value = kwargs.get(attr.original_name) or kwargs.get(attr.local_name)
                setattr(self, attr.local_name, value)
            else:
                setattr(self, attr, kwargs.get(attr))

    @classmethod
    def create(cls, client, **kwargs):
        return cls.__new__(client, kwargs)

    @classmethod
    def handle_list_filters(cls, **kwargs):
        return {}


class TaskList(Resource):
    """Represent a list of tasks"""

    ENDPOINT = "outlook/taskFolders"
    ATTRIBUTES = (
        "id",
        "name",
        AttributeTranslator("changeKey", "_change_key"),
        AttributeTranslator("isDefaultFolder", "is_default"),
        AttributeTranslator("parentGroupKey", "_parent_group_key"),
    )

    def get_tasks(self, status: str = "ne 'completed'"):
        tasks_endpoint = f"{self.ENDPOINT}/{self.id}/tasks"
        return self._client.list(Task, endpoint=tasks_endpoint, status=status)

    def __repr__(self):
        return f"<TaskList '{self.name}'>"

    def __str__(self):
        return f"List '{self.name}'"


class Task(Resource):
    """Represent a task. Listing tasks without specific TaskList returns all tasks"""

    ENDPOINT = "outlook/tasks"
    ATTRIBUTES = (  # TODO: translate & format datas
        "id",
        "body",
        "categories",
        "status",
        "subject",
        "sensitivity",
        "owner",
        "recurrence",
        "importance",
        "assignedTo",
        "changeKey",
        "completedDateTime",
        "createdDateTime",
        "dueDateTime",
        "hasAttachments",
        "isReminderOn",
        "lastModifiedDateTime",
        "parentFolderId",
        "reminderDateTime",
        "startDateTime",
    )

    def __repr__(self):
        return f"<Task '{self.subject}'>"

    def __str__(self):
        return f"Task '{self.subject}'"

    @classmethod
    def handle_list_filters(cls, **kwargs):
        kwargs.setdefault("status", "ne 'completed'")
        params = {"$filter": f"status {kwargs['status']}" if kwargs["status"] else None}
        return params
