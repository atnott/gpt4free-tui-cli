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

@register_tool(
    name="read_project_code",
    description="Read source code files from the project src/ directory. Use this to inspect the codebase.",
    parameters=[
        ToolParameter(name="filepath", type="string", description="Relative path inside src/ (e.g. 'core/engine.py')"),
        ToolParameter(name="max_lines", type="number", description="Maximum lines to read (default 500)", required=False),
    ],
)
def read_project_code(filepath: str, max_lines: int = 500) -> str:
    """Читает файлы из директории src/ проекта.(только текстовые файлы(.py, .txt, .md, .json и т.д.))"""
    current = Path.cwd()
    project_root = None

    for path in [current] + list(current.parents):
        if (path / "src").is_dir() or (path / "pyproject.toml").exists():
            project_root = path
            break

    if not project_root:
        return json.dumps({"error": "Could not find project root (no src/ or pyproject.toml found)"})

    src_dir = project_root / "src"
    if not src_dir.exists():
        return json.dumps({"error": "src/ directory not found in project root"})

    target = (src_dir / filepath).resolve()
    try:
        target.relative_to(src_dir.resolve())
    except ValueError:
        return json.dumps({"error": "Access denied: path escapes src/ directory"})

    if not target.exists():
        return json.dumps({"error": f"File not found: {filepath}"})

    if not target.is_file():
        return json.dumps({"error": f"Not a file: {filepath}"})

    try:
        with open(target, "rb") as f:
            chunk = f.read(8192)
            if b"\x00" in chunk:
                return json.dumps({"error": "Binary files are not supported"})
    except Exception as e:
        return json.dumps({"error": f"Failed to inspect file: {e}"})

    try:
        with open(target, "r", encoding="utf-8") as f:
            lines = f.readlines()

        total = len(lines)
        truncated = total > max_lines
        if truncated:
            lines = lines[:max_lines]

        content = "".join(lines)
        return json.dumps({
            "filepath": str(target.relative_to(project_root)),
            "lines_read": len(lines),
            "total_lines": total,
            "truncated": truncated,
            "content": content,
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": f"Failed to read file: {e}"})

def get_builtin_tools() -> list[Any]:
    """Возвращает список всех встроенных инструментов из глобального реестра."""
    return get_global_registry().list_tools()