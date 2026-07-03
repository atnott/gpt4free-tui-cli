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

class TestChatScreenSwitchToChat:
    """Тесты переключения чата."""

    def test_switch_to_chat_updates_app(self):
        """Обновление текущего chat_id в приложении."""
        screen = ChatScreen()
        screen.app = MagicMock()
        screen.app.current_chat_id = 1

        mock_chat_log = MagicMock()
        screen.query_one = MagicMock(return_value=mock_chat_log)

        screen.app.db.get_all_chat_messages.return_value = []

        screen.switch_to_chat(3)

        assert screen.app.current_chat_id == 3

    def test_switch_to_chat_clears_log(self):
        """Очистка лога при переключении."""
        screen = ChatScreen()
        screen.app = MagicMock()

        mock_chat_log = MagicMock()
        screen.query_one = MagicMock(return_value=mock_chat_log)

        screen.app.db.get_all_chat_messages.return_value = []

        screen.switch_to_chat(1)

        mock_chat_log.query.assert_called_once_with("*")
        mock_chat_log.query.return_value.remove.assert_called_once()

    def test_switch_to_chat_loads_history(self):
        """Загрузка истории сообщений."""
        screen = ChatScreen()
        screen.app = MagicMock()

        mock_chat_log = MagicMock()
        screen.query_one = MagicMock(return_value=mock_chat_log)

        screen.app.db.get_all_chat_messages.return_value = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi!"},
        ]

        screen.switch_to_chat(1)

        assert mock_chat_log.append_message.call_count == 2
        mock_chat_log.append_message.assert_any_call("Hello", is_user=True)
        mock_chat_log.append_message.assert_any_call("Hi!", is_user=False)

    def test_switch_to_chat_updates_active_state(self):
        """Обновление активного состояния элементов чата."""
        screen = ChatScreen()
        screen.app = MagicMock()
        screen.app.current_chat_id = 1
        screen.app.current_chat_title = ""

        mock_chat_log = MagicMock()
        screen.query_one = MagicMock(return_value=mock_chat_log)
        screen.app.db.get_all_chat_messages.return_value = []

        mock_item1 = MagicMock()
        mock_item1.chat_id = 1
        mock_item1.chat_title = "Active Chat"
        mock_item2 = MagicMock()
        mock_item2.chat_id = 2

        screen.query = MagicMock(return_value=[mock_item1, mock_item2])

        mock_btn1 = MagicMock()
        mock_btn2 = MagicMock()
        mock_item1.query_one = MagicMock(return_value=mock_btn1)
        mock_item2.query_one = MagicMock(return_value=mock_btn2)

        screen.switch_to_chat(1)

        mock_btn1.add_class.assert_called_once_with("active-chat")
        mock_btn2.remove_class.assert_called_once_with("active-chat")
        assert screen.app.current_chat_title == "Active Chat"