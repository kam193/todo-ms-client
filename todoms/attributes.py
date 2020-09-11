from enum import Enum


class Importance(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class Status(Enum):
    NOT_STARTED = "notStarted"
    IN_PROGRESS = "inProgress"
    COMPLETED = "completed"
    WAITING_ON_OTHERS = "waitingOnOthers"
    DEFERRED = "deferred"


class RecurrencePatternType(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY_ABSOLUTE = "absoluteMonthly"
    MONTHLY_RELATIVE = "relativeMonthly"
    YEARLY_ABSOLUTE = "absoluteYearly"
    YEARLY_RELATIVE = "relativeYearly"


class RecurrenceRangeType(Enum):
    END_DATE = "endDate"
    NO_END = "noEnd"
    NUMBERED = "numbered"


class Weekday(Enum):
    SUNDAY = "sunday"
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
