from pathlib import Path

import pytest

from gpt4free_tui_cli.core.config import ConfigManager
from gpt4free_tui_cli.core.database import DatabaseManager


@pytest.fixture
def config_manager(tmp_path: Path) -> ConfigManager:
    manager = ConfigManager(filename="test-config.json")
    manager.config_dir = tmp_path / "config"
    manager.config_path = manager.config_dir / "test-config.json"
    return manager


@pytest.fixture
def database_manager(tmp_path: Path) -> DatabaseManager:
    manager = DatabaseManager.__new__(DatabaseManager)
    manager.path_dir = tmp_path
    manager.db_path = tmp_path / "storage.db"
    manager._init_db()
    return manager
