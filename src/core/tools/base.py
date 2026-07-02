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

class ToolRegistry:
    """Реестр инструментов для взаимодействия с моделью."""
    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        """Регистрирует инструмент в реестре."""
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolDefinition | None:
        """Возвращает описание инструмента по имени."""
        return self._tools.get(name)

    def list_tools(self) -> list[ToolDefinition]:
        """Возвращает список всех зарегистрированных инструментов."""
        return list(self._tools.values())
    def get_schemas(self) -> list[dict]:
        """Возвращает список схем инструментов для передачи в LLM."""
        return [tool.to_openai_schema() for tool in self._tools.values()]
    def clear(self) -> None:
        """Очищает реестр инструментов."""
        self._tools.clear()