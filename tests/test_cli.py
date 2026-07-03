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