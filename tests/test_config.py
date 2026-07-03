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

class TestUpdateConfig:
    """Тесты обновления конфигурации."""

    def test_updates_single_value(self, config_manager):
        """Обновление одного значения."""
        config_manager.update_config(last_model="claude-3")
        
        config = config_manager.load_config()
        assert config['last_model'] == "claude-3"
        assert config['last_provider'] is None

    def test_updates_multiple_values(self, config_manager):
        """Обновление нескольких значений."""
        config_manager.update_config(
            last_model="gpt-4o-mini",
            last_provider="Bing",
            current_chat_id=5
        )
        
        config = config_manager.load_config()
        assert config['last_model'] == "gpt-4o-mini"
        assert config['last_provider'] == "Bing"
        assert config['current_chat_id'] == 5

    def test_preserves_existing_values(self, config_manager):
        """Сохранение существующих значений при частичном обновлении."""
        config_manager.update_config(last_model="custom-model")
        config_manager.update_config(current_chat_id=10)
        
        config = config_manager.load_config()
        assert config['last_model'] == "custom-model"
        assert config['current_chat_id'] == 10
        assert config['last_provider'] is None

    def test_creates_config_if_missing_on_update(self, config_manager):
        """Создание конфига при обновлении, если файла нет."""
        assert not config_manager.config_path.exists()
        config_manager.update_config(last_model="test")
        
        assert config_manager.config_path.exists()
        config = config_manager.load_config()
        assert config['last_model'] == "test"

    def test_update_with_empty_kwargs(self, config_manager):
        """Обновление без параметров не ломает конфиг."""
        config_manager._ensure_config_exists()
        config_manager.update_config()
        
        config = config_manager.load_config()
        assert config == config_manager.default_config

class TestConfigFileFormat:
    """Тесты формата файла конфигурации."""

    def test_json_indentation(self, config_manager):
        """Проверка форматирования JSON."""
        config_manager._ensure_config_exists()
        
        with open(config_manager.config_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert '\n' in content
        assert '    ' in content

    def test_utf8_encoding(self, config_manager):
        """Проверка кодировки UTF-8."""
        config_manager.update_config(last_model="тест-модель")
        
        with open(config_manager.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        assert config['last_model'] == "тест-модель"
