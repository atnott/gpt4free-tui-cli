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

@register_tool(
    name="get_random_number",
    description="Generate a random number in range",
    parameters=[
        ToolParameter(name="min", type="number", description="Minimum value", required=False),
        ToolParameter(name="max", type="number", description="Maximum value", required=False),
    ],
)
def get_random_number(min: int = 0, max: int = 100) -> str:
    """Генерирует случайное число в заданном диапазоне."""
    if min > max:
        return "Error: min should not be greater than max"
    return str(random.randint(min, max))

@register_tool(
    name="python_execute",
    description="Execute Python code safely (restricted environment)",
    parameters=[
        ToolParameter(name="code", type="string", description="Python code to execute"),
    ],
)
def python_execute(code: str) -> str:
    """Выполняет Python код в ограниченной среде."""
    import io
    import sys

    stdout = io.StringIO()
    stderr = io.StringIO()

    allowed_builtins = {
        "print": print, "len": len, "range": range,
        "enumerate": enumerate, "zip": zip, "map": map,
        "filter": filter, "sum": sum, "min": min, "max": max,
        "abs": abs, "round": round, "pow": pow,
        "int": int, "float": float, "str": str, "list": list,
        "dict": dict, "set": set, "tuple": tuple,
        "sorted": sorted, "reversed": reversed,
        "math": math, "random": random, "json": json,
        "datetime": datetime,
    }

    try:
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = stdout, stderr
        exec(code, {"__builtins__": allowed_builtins}, {})
        sys.stdout, sys.stderr = old_stdout, old_stderr

        out = stdout.getvalue()
        err = stderr.getvalue()
        if err:
            return f"Output:\n{out}\nErrors:\n{err}"
        return out or "Code executed successfully (no output)"
    except Exception as e:
        sys.stdout, sys.stderr = old_stdout, old_stderr
        return f"Error: {type(e).__name__}: {e}"
