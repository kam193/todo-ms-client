from dataclasses import dataclass

from .patterns import BaseRecurrencePattern


class BaseRecurrenceRange:
    def to_dict(self):
        return {"recurrence": "range"}


@dataclass
class Recurrence:
    pattern: BaseRecurrencePattern
    range: BaseRecurrenceRange

    def to_dict(self):
        return {"pattern": self.pattern.to_dict(), "range": self.range.to_dict()}
