import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
import tempfile
import json
import sqlite3

from core.engine import G4FEngine, ProviderStatus
from core.config import ConfigManager
from core.database import DatabaseManager


@pytest.fixture
def mock_g4f_client():
    """Мок AsyncClient из g4f."""
    with patch("core.engine.AsyncClient") as mock_client_class:
        client = AsyncMock()
        mock_client_class.return_value = client
        yield client


@pytest.fixture
def engine(mock_g4f_client):
    """Инициализированный движок с мок-клиентом."""
    return G4FEngine()


@pytest.fixture
def temp_dir():
    """Временная директория для изолированных тестов."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def config_manager(temp_dir):
    """ConfigManager, работающий во временной директории."""
    config = ConfigManager(filename="test_config.json")
    config.config_dir = temp_dir / ".config" / "gpt4free-tui-cli"
    config.config_path = config.config_dir / "test_config.json"
    return config


@pytest.fixture
def db_manager(temp_dir):
    """DatabaseManager, работающий во временной директории."""
    db = DatabaseManager.__new__(DatabaseManager)
    db.path_dir = temp_dir
    db.db_path = temp_dir / "test_storage.db"
    db._init_db()
    return db


@pytest.fixture
def event_loop():
    """Создание event loop для async тестов."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_app():
    """Мок TUI-приложения для тестов виджетов и менеджера."""
    app = MagicMock()
    app.model = "gpt-4o"
    app.provider = None
    app.current_chat_id = 1
    app.current_chat_title = ""
    app.config = MagicMock()
    app.db = MagicMock()
    app.engine = MagicMock()
    return app


@pytest.fixture
def mock_screen():
    """Мок экрана для тестов."""
    screen = MagicMock()
    screen.query = MagicMock(return_value=[])
    screen.query_one = MagicMock()
    return screen