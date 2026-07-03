import pytest
import json
from pathlib import Path

from core.config import ConfigManager


class TestConfigManagerInitialization:
    """Тесты инициализации."""

    def test_default_config_values(self, config_manager):
        """Проверка дефолтных значений."""
        assert config_manager.default_config == {
            'last_model': 'gpt-4o',
            'last_provider': None,
            'current_chat_id': 1
        }

    def test_config_paths_set_correctly(self, config_manager, temp_dir):
        """Пути конфигурации установлены правильно."""
        assert config_manager.config_dir == temp_dir / ".config" / "gpt4free-tui-cli"
        assert config_manager.config_path == temp_dir / ".config" / "gpt4free-tui-cli" / "test_config.json"
