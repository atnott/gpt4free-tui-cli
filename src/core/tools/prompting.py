import json
from core.tools.base import ToolRegistry
import re

TOOL_CALL_MARKER_START = "<tool_call>"
TOOL_CALL_MARKER_END = "</tool_call>"

def build_tools_system_prompt(registry: ToolRegistry) -> str:
    """Строит системный промпт с описанием инструментов для моделей без нативного function calling."""
    if not registry.list_tools():
        return ""

    schemas = registry.get_schemas()
    tools_json = json.dumps(schemas, ensure_ascii=False, indent=2)

    return f"""У тебя есть доступ к инструментам. Вот их описание в формате JSON-схемы:

{tools_json}

Если для ответа на вопрос пользователя нужен инструмент — верни ТОЛЬКО один блок в формате:
{TOOL_CALL_MARKER_START}
{{"name": "имя_инструмента", "arguments": {{"параметр": "значение"}}}}
{TOOL_CALL_MARKER_END}

ПРИМЕР 1:
Пользователь: вычисли 15 * 4
Ты: {TOOL_CALL_MARKER_START}{{"name": "calculator", "arguments": {{"expression": "15 * 4"}}}}{TOOL_CALL_MARKER_END}

ПРИМЕР 2:
Пользователь: привет, как дела?
Ты: Привет! Всё отлично. Чем могу помочь?

КРИТИЧЕСКИ ВАЖНО: Никакого текста до или после блока <tool_call>, если ты вызываешь инструмент! Не пиши "Готово" или "Вызываю инструмент". Выводи ТОЛЬКО блок."""


TOOL_CALL_RE = re.compile(
    rf"{re.escape(TOOL_CALL_MARKER_START)}\s*(\{{.*?\}})\s*{re.escape(TOOL_CALL_MARKER_END)}",
    re.DOTALL,
)

def extract_tool_call(buffer: str) -> dict | None:
    """Пытается найти завершённый блок вызова инструмента в накопленном тексте."""
    match = TOOL_CALL_RE.search(buffer)
    if not match:
        return None
    try:
        payload = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None

    return {
        "id": f"call_{abs(hash(match.group(1))) % 10**8}",
        "type": "function",
        "function": {
            "name": payload.get("name", ""),
            "arguments": json.dumps(payload.get("arguments", {}), ensure_ascii=False),
        },
    }

def has_open_tool_call(buffer: str) -> bool:
    """True, если в буфере есть начало блока, но конца ещё нет (стрим не завершён)."""
    return TOOL_CALL_MARKER_START in buffer and TOOL_CALL_MARKER_END not in buffer

def is_safe_to_stream(buffer: str) -> bool:
    """True, если в буфере точно нет вызова инструмента — можно смело стримить в UI."""
    return TOOL_CALL_MARKER_START not in buffer