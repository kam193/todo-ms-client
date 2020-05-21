from typing import Callable, Any
from dataclasses import dataclass


@dataclass
class AttributeConverter:
    original_name: str
    local_name: str
    obj_converter: Callable[[Any], Any] = lambda x: x
