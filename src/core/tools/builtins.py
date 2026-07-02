import json
import math
import random
import datetime
from pathlib import Path
from typing import Any
from core.tools.base import register_tool, ToolParameter, get_global_registry

@register_tool(
    name="calculator",
    description="Evaluate mathematical expressions safely",
    parameters=[
        ToolParameter(name="expression", type="string", description="Math expression like '2 + 2 * 3'"),
    ],
)
def calculator(expression: str) -> str:
    """Калькулятор на eval с безопасной обработкой выражений."""
    allowed_names = {
        "abs": abs, "max": max, "min": min, "sum": sum,
        "pow": pow, "round": round, "len": len,
        "math": math, "random": random,
        "pi": math.pi, "e": math.e,
    }
    try:
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return str(result)
    except Exception as e:
        return f"Error: {e}"
    
@register_tool(
     name="get_current_time",
    description="Get current date and time",
    parameters=[],
)
def get_current_time() -> str:
    """Возвращает текущие дату и время в формате YYYY-MM-DD HH:MM:SS (Weekday)."""
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S (%A)")
