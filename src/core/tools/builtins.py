import json
import math
import random
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
def calulator(expression: str) -> str:
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