from enum import Enum


class Importance(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class Sensitivity(Enum):
    NORMAL = "normal"
    PERSONAL = "personal"
    PRIVATE = "private"
    CONFIDENTIAL = "confidential"


class Status(Enum):
    NOT_STARTED = "notStarted"
    IN_PROGRESS = "inProgress"
    COMPLETED = "completed"
    WAITING_ON_OTHERS = "waitingOnOthers"
    DEFERRED = "deferred"
