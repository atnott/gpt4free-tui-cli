import pytest
from unittest.mock import MagicMock, patch, PropertyMock

from textual.widgets import Static, Input, Button
from rich.markdown import Markdown as RichMarkdown

from tui.widgets.header import AppHeader
from tui.widgets.user_message import UserMessage
from tui.widgets.bot_loading import BotLoading
from tui.widgets.bot_message import BotMessage
from tui.widgets.chat_log import ChatLog
from tui.widgets.chat_item import ChatItem
from tui.widgets.chats_sidebar import ChatSidebar
from tui.widgets.choose_panel import ChoosePanel
from tui.widgets.chat_input import ChatInput


class TestAppHeader:
    """Тесты хедера."""

    def test_compose_structure(self):
        """Структура компоновки."""
        header = AppHeader(id="Header")
        children = list(header.compose())

        assert len(children) == 3

    def test_on_mount_watches_model(self):
        """Подписка на изменение model."""
        header = AppHeader()
        mock_app = MagicMock()
        header.app = mock_app

        with patch.object(header, "watch") as mock_watch:
            header.on_mount()

        mock_watch.assert_any_call(mock_app, "model", header.update_model_label)

    def test_on_mount_watches_chat_title(self):
        """Подписка на изменение current_chat_title."""
        header = AppHeader()
        mock_app = MagicMock()
        header.app = mock_app

        with patch.object(header, "watch") as mock_watch:
            header.on_mount()

        mock_watch.assert_any_call(mock_app, "current_chat_title", header.update_chat_title)

    def test_update_model_label(self):
        """Обновление label модели."""
        header = AppHeader()
        mock_label = MagicMock()
        header.query_one = MagicMock(return_value=mock_label)

        header.update_model_label("gpt-4o")

        mock_label.update.assert_called_once_with("GPT-4O")

    def test_update_model_label_error(self):
        """Обработка ошибки при обновлении label модели."""
        header = AppHeader()
        header.query_one = MagicMock(side_effect=Exception("Not found"))

        header.update_model_label("gpt-4o")

    def test_update_chat_title(self):
        """Обновление заголовка чата."""
        header = AppHeader()
        mock_label = MagicMock()
        header.query_one = MagicMock(return_value=mock_label)

        header.update_chat_title("My Chat")

        mock_label.update.assert_called_once_with("My Chat")

class TestUserMessage:
    """Тесты сообщения пользователя."""

    def test_init(self):
        """Инициализация."""
        msg = UserMessage("Hello")
        assert msg.text == "Hello"

    def test_compose(self):
        """Компоновка содержит Static с текстом."""
        msg = UserMessage("Test message")
        children = list(msg.compose())

        assert len(children) == 1
        assert isinstance(children[0], Static)
        assert children[0].renderable == "Test message"