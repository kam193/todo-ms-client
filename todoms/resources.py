from abc import ABC

from .converters import AttributeConverter


class Resource(ABC):
    """Base Resource for any other"""

    ENDPOINT = ""
    ATTRIBUTES = ()

    def __init__(self, client, **kwargs):
        self._client = client
        for attr in self.ATTRIBUTES:
            if isinstance(attr, AttributeConverter):
                value = kwargs.get(attr.original_name) or kwargs.get(attr.local_name)
                setattr(self, attr.local_name, attr.obj_converter(value))
            else:
                setattr(self, attr, kwargs.get(attr))

    @classmethod
    def create(cls, client, **kwargs):
        return cls(client, **kwargs)

    @classmethod
    def handle_list_filters(cls, **kwargs):
        return {}


class TaskList(Resource):
    """Represent a list of tasks"""

    ENDPOINT = "outlook/taskFolders"
    ATTRIBUTES = (
        "id",
        "name",
        AttributeConverter("changeKey", "_change_key"),
        AttributeConverter("isDefaultFolder", "is_default"),
        AttributeConverter("parentGroupKey", "_parent_group_key"),
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
    ATTRIBUTES = (  # TODO: translate & format dates
        "id",
        "body",
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
        AttributeConverter("changeKey", "_change_key"),
        AttributeConverter("completedDateTime", "completed_datetime"),
        AttributeConverter("createdDateTime", "created_datetime"),
        AttributeConverter("dueDateTime", "due_datetime"),
        AttributeConverter("lastModifiedDateTime", "last_modified_datetime"),
        AttributeConverter("reminderDateTime", "reminder_datetime"),
        AttributeConverter("startDateTime", "start_datetime"),
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
