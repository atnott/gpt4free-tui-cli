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

@dataclass
class ToolDefinition:
    """Описание инструмента."""
    name: str
    description: str
    parameters: list[ToolParameter] = field(default_factory=list)
    func: Callable | None = None

    def to_openai_schema(self) -> dict:
        """Конвертирует описание инструмента в формат OpenAI Fuction Calling."""
        properties = {}
        required = []
        for param in self.parameters:
            prop = {"type": param.type, "description": param.description}
            if param.enum is not None:
                prop["enum"] = param.enum
            properties[param.name] = prop
            if param.required:
                required.append(param.name)
        return {
            "type" : "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }
