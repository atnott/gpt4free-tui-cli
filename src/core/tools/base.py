import json
import inspect
from typing import Any, Callable
from dataclasses import dataclass, field

@dataclass
class ToolParameter:
    """Описание параметра инструмента."""
    name: str
    type: str
    description: str
    required: bool = True
    enum: list[Any] | None = None
