"""Composition root приложения.

Только этот модуль создаёт concrete adapters для CLI и TUI.
"""

from dataclasses import dataclass

from gpt4free_tui_cli.adapters.persistence.sqlite import SQLiteChatRepository
from gpt4free_tui_cli.adapters.providers.g4f import G4FCatalog, G4FModelProvider
from gpt4free_tui_cli.adapters.settings.json_file import JsonSettings
from gpt4free_tui_cli.application.chat_service import ChatService
from gpt4free_tui_cli.core.config import ConfigManager
from gpt4free_tui_cli.core.database import DatabaseManager
from gpt4free_tui_cli.tui.tui_core.chat_manager import ChatManager


@dataclass(slots=True)
class ApplicationDependencies:
    chat_service: ChatService
    catalog: G4FCatalog
    config: ConfigManager
    db: DatabaseManager
    chat_manager: ChatManager


def create_catalog() -> G4FCatalog:
    """Создать каталог моделей для read-only команд."""
    return G4FCatalog()


def create_application_dependencies() -> ApplicationDependencies:
    """Создать зависимости, которым нужны пользовательские данные."""
    config = ConfigManager()
    database = DatabaseManager()
    return ApplicationDependencies(
        chat_service=ChatService(
            provider=G4FModelProvider(),
            chats=SQLiteChatRepository(database),
            settings=JsonSettings(config),
        ),
        catalog=create_catalog(),
        config=config,
        db=database,
        chat_manager=ChatManager(),
    )
