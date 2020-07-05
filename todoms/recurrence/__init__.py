from dataclasses import dataclass

from ..convertable import BaseConvertableObject
from .patterns import BaseRecurrencePattern
from .ranges import BaseRecurrenceRange


@dataclass
class Recurrence(BaseConvertableObject):
    pattern: BaseRecurrencePattern
    range: BaseRecurrenceRange

    def to_dict(self):
        return {"pattern": self.pattern.to_dict(), "range": self.range.to_dict()}
