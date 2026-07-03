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