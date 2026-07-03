import pytest
from unittest.mock import MagicMock, patch

from tui.screens.chat import ChatScreen


class TestChatScreenCompose:
    """Тесты компоновки ChatScreen."""

    def test_compose_structure(self):
        """Структура экрана."""
        screen = ChatScreen()
        children = list(screen.compose())

        assert len(children) == 5

class TestChatScreenOnMount:
    """Тесты on_mount."""

    def test_on_mount_with_chat_id(self):
        """Загрузка истории при наличии chat_id."""
        screen = ChatScreen()
        screen.app = MagicMock()
        screen.app.current_chat_id = 5

        screen.switch_to_chat = MagicMock()

        screen.on_mount()

        screen.switch_to_chat.assert_called_once_with(5)

    def test_on_mount_without_chat_id(self):
        """Без chat_id — ничего не загружается."""
        screen = ChatScreen()
        screen.app = MagicMock()
        screen.app.current_chat_id = None

        screen.switch_to_chat = MagicMock()

        screen.on_mount()

        screen.switch_to_chat.assert_not_called()
