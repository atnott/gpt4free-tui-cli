import ast
from pathlib import Path


def test_domain_and_application_do_not_import_framework_or_adapter_modules() -> None:
    source_root = Path("src/gpt4free_tui_cli")
    forbidden_roots = {"g4f", "textual", "typer", "rich", "sqlite3", "pathlib"}

    for package in ("domain", "application"):
        for path in (source_root / package).glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            imported_roots = {
                alias.name.split(".")[0]
                for node in ast.walk(tree)
                if isinstance(node, (ast.Import, ast.ImportFrom))
                for alias in node.names
            }
            assert not imported_roots & forbidden_roots, path
