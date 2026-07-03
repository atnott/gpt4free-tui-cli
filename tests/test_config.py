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

class TestEnsureConfigExists:
    """Тесты создания конфигурации."""

    def test_creates_directory_if_not_exists(self, config_manager):
        """Создание директории при отсутствии."""
        assert not config_manager.config_dir.exists()
        config_manager._ensure_config_exists()
        assert config_manager.config_dir.exists()

    def test_creates_file_with_defaults(self, config_manager):
        """Создание файла с дефолтными настройками."""
        config_manager._ensure_config_exists()
        assert config_manager.config_path.exists()

        with open(config_manager.config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert data == config_manager.default_config

    def test_does_not_overwrite_existing(self, config_manager):
        """Не перезаписывает существующий файл."""
        config_manager._ensure_config_exists()
        
        # Меняем содержимое
        with open(config_manager.config_path, 'w', encoding='utf-8') as f:
            json.dump({"custom": "value"}, f)

        config_manager._ensure_config_exists()
        
        with open(config_manager.config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert data == {"custom": "value"}

class TestLoadConfig:
    """Тесты загрузки конфигурации."""

    def test_loads_existing_config(self, config_manager):
        """Загрузка существующего конфига."""
        config_manager._ensure_config_exists()
        config = config_manager.load_config()
        assert config['last_model'] == 'gpt-4o'
        assert config['current_chat_id'] == 1

    def test_creates_and_loads_if_missing(self, config_manager):
        """Создание и загрузка при отсутствии файла."""
        assert not config_manager.config_path.exists()
        config = config_manager.load_config()
        assert config == config_manager.default_config
        assert config_manager.config_path.exists()
