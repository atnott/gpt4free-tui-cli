import pytest
from unittest.mock import MagicMock, patch

from textual.app import App
from textual._context import active_app

from tui.screens.chat import ChatScreen


@pytest.fixture
def app_context():
    """Создаёт Textual App с активным контекстом и нужными атрибутами."""
    app = App()
    app._compose_stacks = [[], [], []]
    app._composed = [[]]
    app.current_chat_id = None
    app.current_chat_title = ""
    app.db = MagicMock()
    token = active_app.set(app)
    try:
        yield app
    finally:
        active_app.reset(token)


class TestChatScreenCompose:
    """Тесты компоновки ChatScreen."""

    def test_compose_structure(self, app_context):
        """Структура экрана."""
        screen = ChatScreen()
        screen._app = app_context
        children = list(screen.compose())
        # AppHeader, ChatSidebar, ChatLog, ChatInput, ChoosePanel, Footer
        assert len(children) == 6


class TestChatScreenOnMount:
    """Тесты on_mount."""

    def test_on_mount_with_chat_id(self, app_context):
        """Загрузка истории при наличии chat_id."""
        screen = ChatScreen()
        app_context.current_chat_id = 5
        screen._app = app_context
        screen.switch_to_chat = MagicMock()
        screen.on_mount()
        screen.switch_to_chat.assert_called_once_with(5)

    def test_on_mount_without_chat_id(self, app_context):
        """Без chat_id — ничего не загружается."""
        screen = ChatScreen()
        app_context.current_chat_id = None
        screen._app = app_context
        screen.switch_to_chat = MagicMock()
        screen.on_mount()
        screen.switch_to_chat.assert_not_called()


class TestChatScreenSwitchToChat:
    """Тесты переключения чата."""

    def test_switch_to_chat_updates_app(self, app_context):
        """Обновление текущего chat_id в приложении."""
        screen = ChatScreen()
        app_context.current_chat_id = 1
        screen._app = app_context
        mock_chat_log = MagicMock()
        screen.query_one = MagicMock(return_value=mock_chat_log)
        app_context.db.get_all_chat_messages.return_value = []
        screen.switch_to_chat(3)
        assert screen.app.current_chat_id == 3

    def test_switch_to_chat_clears_log(self, app_context):
        """Очистка лога при переключении."""
        screen = ChatScreen()
        screen._app = app_context
        mock_chat_log = MagicMock()
        screen.query_one = MagicMock(return_value=mock_chat_log)
        app_context.db.get_all_chat_messages.return_value = []
        screen.switch_to_chat(1)
        mock_chat_log.query.assert_called_once_with("*")
        mock_chat_log.query.return_value.remove.assert_called_once()

    def test_switch_to_chat_loads_history(self, app_context):
        """Загрузка истории сообщений."""
        screen = ChatScreen()
        screen._app = app_context
        mock_chat_log = MagicMock()
        screen.query_one = MagicMock(return_value=mock_chat_log)
        app_context.db.get_all_chat_messages.return_value = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi!"},
        ]
        screen.switch_to_chat(1)
        assert mock_chat_log.append_message.call_count == 2
        mock_chat_log.append_message.assert_any_call("Hello", is_user=True)
        mock_chat_log.append_message.assert_any_call("Hi!", is_user=False)

    def test_switch_to_chat_updates_active_state(self, app_context):
        """Обновление активного состояния элементов чата."""
        screen = ChatScreen()
        app_context.current_chat_id = 1
        app_context.current_chat_title = ""
        screen._app = app_context
        mock_chat_log = MagicMock()
        screen.query_one = MagicMock(return_value=mock_chat_log)
        app_context.db.get_all_chat_messages.return_value = []
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