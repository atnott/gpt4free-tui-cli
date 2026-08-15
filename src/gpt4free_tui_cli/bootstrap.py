"""Composition root приложения.

Только этот модуль создаёт concrete adapters для CLI и TUI.
"""

from dataclasses import dataclass

from gpt4free_tui_cli.core.config import ConfigManager
from gpt4free_tui_cli.core.database import DatabaseManager
from gpt4free_tui_cli.core.engine import G4FEngine
from gpt4free_tui_cli.tui.tui_core.chat_manager import ChatManager


@dataclass(slots=True)
class ApplicationDependencies:
    engine: G4FEngine
    config: ConfigManager
    db: DatabaseManager
    chat_manager: ChatManager


def create_engine() -> G4FEngine:
    """Создать adapter провайдера для read-only команд каталога."""
    return G4FEngine()


def create_application_dependencies() -> ApplicationDependencies:
    """Создать зависимости, которым нужны пользовательские данные."""
    return ApplicationDependencies(
        engine=create_engine(),
        config=ConfigManager(),
        db=DatabaseManager(),
        chat_manager=ChatManager(),
    )
