import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from typer.testing import CliRunner
import asyncio

from cli import app, stream_response


runner = CliRunner()


class TestMainCommand:
    """Тесты главной команды (чат)."""

    @patch("cli.engine")
    @patch("cli.config")
    @patch("cli.db")
    def test_main_with_prompt(self, mock_db, mock_config, mock_engine):
        """Базовый запрос с промптом."""
        mock_config.load_config.return_value = {
            'last_model': 'gpt-4o',
            'last_provider': None,
            'current_chat_id': 1
        }
        mock_db.get_chat_history.return_value = []
        
        # Мокаем stream_response чтобы не ждать реального выполнения
        with patch("cli.stream_response") as mock_stream:
            mock_stream.return_value = None
            
            result = runner.invoke(app, ["--prompt", "Привет!"])
            
            assert result.exit_code == 0
            assert "Запрос к модели" in result.output
            assert "[gpt-4o]" in result.output
            mock_db.save_message.assert_called_once_with(
                chat_id=1, role='user', content='Привет!'
            )

    @patch("cli.engine")
    @patch("cli.config")
    @patch("cli.db")
    def test_main_with_custom_model(self, mock_db, mock_config, mock_engine):
        """Запрос с указанием модели."""
        mock_config.load_config.return_value = {}
        mock_db.get_chat_history.return_value = []
        
        with patch("cli.stream_response"):
            result = runner.invoke(app, [
                "--prompt", "Test",
                "--model", "claude-3"
            ])
            
            assert result.exit_code == 0
            assert "[claude-3]" in result.output

    @patch("cli.engine")
    @patch("cli.config")
    @patch("cli.db")
    def test_main_with_provider(self, mock_db, mock_config, mock_engine):
        """Запрос с указанием провайдера."""
        mock_config.load_config.return_value = {}
        mock_db.get_chat_history.return_value = []
        
        with patch("cli.stream_response"):
            result = runner.invoke(app, [
                "--prompt", "Test",
                "--provider", "Bing"
            ])
            
            assert result.exit_code == 0
            assert "[Bing]" in result.output

    @patch("cli.engine")
    @patch("cli.config")
    @patch("cli.db")
    def test_main_with_web_search(self, mock_db, mock_config, mock_engine):
        """Запрос с веб-поиском."""
        mock_config.load_config.return_value = {}
        mock_db.get_chat_history.return_value = []
        
        with patch("cli.stream_response") as mock_stream:
            result = runner.invoke(app, [
                "--prompt", "Новости",
                "--web"
            ])
            
            assert result.exit_code == 0
            assert "с поиском в сети" in result.output

    @patch("cli.engine")
    @patch("cli.config")
    @patch("cli.db")
    def test_main_with_chat_id(self, mock_db, mock_config, mock_engine):
        """Запрос с указанием chat_id."""
        mock_config.load_config.return_value = {}
        mock_db.get_chat_history.return_value = []
        
        with patch("cli.stream_response"):
            result = runner.invoke(app, [
                "--prompt", "Test",
                "--id", "5"
            ])
            
            assert result.exit_code == 0
            assert "[ID: 5]" in result.output
            mock_db.save_message.assert_called_once_with(
                chat_id=5, role='user', content='Test'
            )

    @patch("cli.engine")
    @patch("cli.config")
    @patch("cli.db")
    def test_main_uses_config_defaults(self, mock_db, mock_config, mock_engine):
        """Использование значений из конфига."""
        mock_config.load_config.return_value = {
            'last_model': 'gpt-4o-mini',
            'last_provider': 'OpenaiChat',
            'current_chat_id': 3
        }
        mock_db.get_chat_history.return_value = []
        
        with patch("cli.stream_response"):
            result = runner.invoke(app, ["--prompt", "Test"])
            
            assert "[gpt-4o-mini]" in result.output
            assert "[OpenaiChat]" in result.output
            assert "[ID: 3]" in result.output

    @patch("cli.engine")
    @patch("cli.config")
    @patch("cli.db")
    def test_main_without_prompt(self, mock_db, mock_config, mock_engine):
        """Запуск без промпта (должен вывести 'tui')."""
        result = runner.invoke(app)
        
        assert result.exit_code == 0
        assert "tui" in result.output

    @patch("cli.engine")
    @patch("cli.config")
    @patch("cli.db")
    def test_main_formats_history(self, mock_db, mock_config, mock_engine):
        """Форматирование истории сообщений."""
        mock_config.load_config.return_value = {}
        mock_db.get_chat_history.return_value = [
            {'role': 'user', 'content': 'Q1'},
            {'role': 'assistant', 'content': 'A1'},
        ]
        
        with patch("cli.stream_response") as mock_stream:
            runner.invoke(app, ["--prompt", "Test"])
            
            call_args = mock_stream.call_args
            messages = call_args.kwargs['messages']
            assert messages == [
                {'role': 'user', 'content': 'Q1'},
                {'role': 'assistant', 'content': 'A1'},
            ]

class TestListModelsCommand:
    """Тесты команды models."""

    @patch("cli.engine")
    @patch("cli.console")
    def test_list_models(self, mock_console, mock_engine):
        """Вывод списка моделей."""
        mock_engine.get_all_models.return_value = ["gpt-4o", "claude-3", "llama-3"]
        
        result = runner.invoke(app, ["models"])
        
        assert result.exit_code == 0
        mock_console.print.assert_called_once()
        table = mock_console.print.call_args[0][0]
        assert "gpt-4o" in str(table.render())
        assert "claude-3" in str(table.render())

    @patch("cli.engine")
    def test_list_models_empty(self, mock_engine):
        """Пустой список моделей."""
        mock_engine.get_all_models.return_value = []
        
        result = runner.invoke(app, ["models"])
        assert result.exit_code == 0

class TestListProvidersCommand:
    """Тесты команды providers."""

    @patch("cli.engine")
    @patch("cli.console")
    def test_list_providers(self, mock_console, mock_engine):
        """Вывод списка провайдеров."""
        mock_provider1 = MagicMock()
        mock_provider1.name = "ProviderA"
        mock_provider1.supported_models = ["gpt-4o", "claude-3"]
        
        mock_provider2 = MagicMock()
        mock_provider2.name = "ProviderB"
        mock_provider2.supported_models = ["gpt-4o-mini"]
        
        mock_engine.get_available_providers.return_value = [mock_provider1, mock_provider2]
        
        result = runner.invoke(app, ["providers"])
        
        assert result.exit_code == 0
        mock_console.print.assert_called_once()

    @patch("cli.engine")
    def test_list_providers_empty(self, mock_engine):
        """Пустой список провайдеров."""
        mock_engine.get_available_providers.return_value = []
        
        result = runner.invoke(app, ["providers"])
        assert result.exit_code == 0

class TestListChatsCommand:
    """Тесты команды chats."""

    @patch("cli.db")
    @patch("cli.config")
    @patch("cli.console")
    def test_list_chats(self, mock_console, mock_config, mock_db):
        """Вывод списка чатов."""
        mock_db.get_all_chats.return_value = [
            {'id': 1, 'title': 'Chat 1', 'created_at': '2024-01-01'},
            {'id': 2, 'title': 'Chat 2', 'created_at': '2024-01-02'},
        ]
        mock_config.load_config.return_value = {'current_chat_id': 1}
        
        result = runner.invoke(app, ["chats"])
        
        assert result.exit_code == 0
        mock_console.print.assert_called_once()

    @patch("cli.db")
    @patch("cli.console")
    def test_list_chats_empty(self, mock_console, mock_db):
        """Пустой список чатов."""
        mock_db.get_all_chats.return_value = []
        
        result = runner.invoke(app, ["chats"])
        
        assert result.exit_code == 0
        assert "нет созданных чатов" in result.output

    @patch("cli.db")
    @patch("cli.config")
    @patch("cli.console")
    def test_list_chats_highlights_active(self, mock_console, mock_config, mock_db):
        """Подсветка активного чата."""
        mock_db.get_all_chats.return_value = [
            {'id': 1, 'title': 'Active', 'created_at': '2024-01-01'},
            {'id': 2, 'title': 'Inactive', 'created_at': '2024-01-02'},
        ]
        mock_config.load_config.return_value = {'current_chat_id': 1}
        
        result = runner.invoke(app, ["chats"])
        
        assert result.exit_code == 0

        table = mock_console.print.call_args[0][0]
        table_str = str(table.render())
        assert "Active" in table_str

class TestNewChatCommand:
    """Тесты команды new-chat."""

    @patch("cli.db")
    @patch("cli.config")
    @patch("cli.console")
    def test_create_new_chat(self, mock_console, mock_config, mock_db):
        """Создание нового чата."""
        mock_db.create_chat.return_value = 5
        
        result = runner.invoke(app, ["new-chat", "My New Chat"])
        
        assert result.exit_code == 0
        mock_db.create_chat.assert_called_once_with(title="My New Chat")
        mock_config.update_config.assert_called_once_with(current_chat_id=5)
        assert "успешно создан" in result.output
        assert "id: 5" in result.output

    @patch("cli.db")
    @patch("cli.config")
    @patch("cli.console")
    def test_create_new_chat_default_title(self, mock_console, mock_config, mock_db):
        """Создание чата с названием по умолчанию."""
        mock_db.create_chat.return_value = 2
        
        result = runner.invoke(app, ["new-chat"])
        
        assert result.exit_code == 0
        mock_db.create_chat.assert_called_once_with(title="Название по умолчанию")

class TestSelectChatCommand:
    """Тесты команды select-chat."""

    @patch("cli.db")
    @patch("cli.config")
    @patch("cli.console")
    def test_select_existing_chat(self, mock_console, mock_config, mock_db):
        """Выбор существующего чата."""
        mock_db.get_all_chats.return_value = [
            {'id': 1, 'title': 'Chat 1'},
            {'id': 2, 'title': 'Chat 2'},
        ]
        
        result = runner.invoke(app, ["select-chat", "2"])
        
        assert result.exit_code == 0
        mock_config.update_config.assert_called_once_with(current_chat_id=2)
        assert "Успешно переключено" in result.output

    @patch("cli.db")
    @patch("cli.config")
    @patch("cli.console")
    def test_select_nonexistent_chat(self, mock_console, mock_config, mock_db):
        """Выбор несуществующего чата."""
        mock_db.get_all_chats.return_value = [
            {'id': 1, 'title': 'Chat 1'},
        ]
        
        result = runner.invoke(app, ["select-chat", "999"])
        
        assert result.exit_code == 0
        assert "Ошибка" in result.output
        assert "не существует" in result.output
        mock_config.update_config.assert_not_called()