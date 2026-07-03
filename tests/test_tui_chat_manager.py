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

class TestCreateNewChat:
    """Тесты создания чата."""

    def test_create_new_chat(self, mock_app, mock_screen):
        """Создание нового чата."""
        manager = ChatManager()

        mock_app.db.create_chat.return_value = 5

        mock_chat_list = MagicMock()
        mock_screen.query_one.return_value = mock_chat_list

        with patch("tui.tui_core.chat_manager.ChatItem") as mock_chat_item_class:
            mock_item = MagicMock()
            mock_chat_item_class.return_value = mock_item

            result = manager.create_new_chat(mock_app, mock_screen, "Test Chat")

        mock_app.db.create_chat.assert_called_once_with("Test Chat")
        mock_chat_item_class.assert_called_once_with(chat_id=5, title="Test Chat")
        mock_chat_list.mount.assert_called_once_with(mock_item)
        mock_screen.switch_to_chat.assert_called_once_with(5)
        assert result == 5

    def test_create_new_chat_default_title(self, mock_app, mock_screen):
        """Создание чата с названием по умолчанию."""
        manager = ChatManager()

        mock_app.db.create_chat.return_value = 2
        mock_chat_list = MagicMock()
        mock_screen.query_one.return_value = mock_chat_list

        with patch("tui.tui_core.chat_manager.ChatItem") as mock_chat_item_class:
            mock_item = MagicMock()
            mock_chat_item_class.return_value = mock_item

            manager.create_new_chat(mock_app, mock_screen)

        mock_app.db.create_chat.assert_called_once_with("New Chat")

class TestDeleteChat:
    """Тесты удаления чата."""

    def test_delete_chat_not_current(self, mock_app, mock_screen):
        """Удаление неактивного чата."""
        manager = ChatManager()

        mock_app.current_chat_id = 1
        mock_item = MagicMock()
        mock_item.chat_id = 2

        manager.delete_chat(mock_app, mock_screen, mock_item)

        mock_app.db.delete_chat.assert_called_once_with(2)
        mock_item.remove.assert_called_once()
        mock_screen.switch_to_chat.assert_not_called()

    def test_delete_current_chat_with_remaining(self, mock_app, mock_screen):
        """Удаление активного чата, есть другие чаты."""
        manager = ChatManager()

        mock_app.current_chat_id = 2

        mock_item1 = MagicMock()
        mock_item1.chat_id = 1
        mock_item2 = MagicMock()
        mock_item2.chat_id = 2  # текущий

        mock_screen.query.return_value = [mock_item1, mock_item2]

        manager.delete_chat(mock_app, mock_screen, mock_item2)

        mock_app.db.delete_chat.assert_called_once_with(2)
        mock_screen.switch_to_chat.assert_called_once_with(1)
        mock_item2.remove.assert_called_once()

    def test_delete_current_chat_last_one(self, mock_app, mock_screen):
        """Удаление последнего чата — создаётся новый."""
        manager = ChatManager()

        mock_app.current_chat_id = 1

        mock_item = MagicMock()
        mock_item.chat_id = 1

        mock_screen.query.return_value = [mock_item]

        with patch.object(manager, "create_new_chat") as mock_create:
            manager.delete_chat(mock_app, mock_screen, mock_item)

        mock_app.db.delete_chat.assert_called_once_with(1)
        mock_create.assert_called_once_with(mock_app, mock_screen, "New Chat")
        mock_item.remove.assert_called_once()
