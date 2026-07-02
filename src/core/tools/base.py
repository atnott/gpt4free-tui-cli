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

class ToolExecutor:
    """Выполняет вызовы инструментов, полученные от модели."""
    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry
    async def execute(self, tool_call: dict) -> dict:
        """Выполняет один вызов(tool_call) и возвращает результат."""
        func_name = tool_call.get("function", {}).get("name")
        arguments_raw = tool_call.get("function", {}).get("arguments", "{}")

        tool_def = self.registry.get(func_name)
        if not tool_def:
            return {"tool_call_id": tool_call.get("id"),
                "role": "tool",
                "name": func_name,
                "content": json.dumps({"error": f"Tool '{func_name}' not found"}),
            }
        try:
            args = json.loads(arguments_raw) if isinstance(arguments_raw, str) else arguments_raw
        except json.JSONDecodeError:
            return {
                "tool_call_id": tool_call.get("id"),
                "role": "tool",
                "name": func_name,
                "content": json.dumps({"error": "Invalid JSON arguments"}),
            }
        try:
            func = tool_def.func
            if func is None:
                raise RuntimeError("Tool function is None")

            if inspect.iscoroutinefunction(func):
                result = await func(**args)
            else:
                result = func(**args)

            if not isinstance(result, str):
                result = json.dumps(result, ensure_ascii=False, default=str)

            return {
                "tool_call_id": tool_call.get("id"),
                "role": "tool",
                "name": func_name,
                "content": str(result),
            }
        except Exception as e:
            return {
                "tool_call_id": tool_call.get("id"),
                "role": "tool",
                "name": func_name,
                "content": json.dumps({"error": str(e)}),
            }

@dataclass
class ChatResult:
    """Результат выполнения чата, включая сообщения и ошибки."""
    content: str
    tools_enabled: bool
    fallback_to_no_tools: bool = False
    warning: str | None = None

def tool(
        name: str | None = None,
        description: str | None = None,
        parameters: list[ToolParameter] | None = None,
):
    """Декоратор для регистрации функции как инструмента."""
    def decorator(func: Callable) -> Callable:
        tool_name = name or func.__name__
        tool_desc = description or (func.__doc__ or f"Execute {tool_name}")

        params = parameters or []
        if not parameters:
            sig = inspect.signature(func)
            for param_name, param in sig.parameters.items():
                if param_name == "return":
                    continue
                param_type = "string"
                if param.annotation != inspect.Parameter.empty:
                    if param.annotation in (int, float):
                        param_type = "number"
                    elif param.annotation == bool:
                        param_type = "boolean"
                    elif param.annotation == list:
                        param_type = "array"
                    elif param.annotation == dict:
                        param_type = "object"
                params.append(
                    ToolParameter(
                        name=param_name,
                        type=param_type,
                        description=f"Parameter {param_name}",
                        required=param.default == inspect.Parameter.empty,
                    )
                )

        defn = ToolDefinition(
            name=tool_name,
            description=tool_desc,
            parameters=params,
            func=func,
        )
        func._tool_definition = defn
        return func

    return decorator