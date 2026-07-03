import pytest
from unittest.mock import MagicMock, patch

from tui.tui_core.chat_manager import ChatManager
from tui.widgets.chat_item import ChatItem


class TestChatManagerInitialization:
    """Тесты инициализации."""

    def test_init(self):
        """Простая инициализация."""
        manager = ChatManager()
        assert manager is not None
