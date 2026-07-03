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

class TestBotLoading:
    """Тесты индикатора загрузки."""

    def test_on_mount_sets_frames(self):
        """Установка фреймов при монтировании."""
        loading = BotLoading()
        loading.set_interval = MagicMock()
        loading.update = MagicMock()

        loading.on_mount()

        assert len(loading.frames) == 10
        assert loading.idx == 0
        loading.set_interval.assert_called_once_with(0.08, loading.update_spinner)

    def test_update_spinner(self):
        """Обновление спиннера."""
        loading = BotLoading()
        loading.frames = ["A", "B", "C"]
        loading.idx = 0
        loading.update = MagicMock()

        loading.update_spinner()

        loading.update.assert_called_once_with("A")
        assert loading.idx == 1

    def test_update_spinner_wraps(self):
        """Циклическое обновление спиннера."""
        loading = BotLoading()
        loading.frames = ["A", "B"]
        loading.idx = 1
        loading.update = MagicMock()

        loading.update_spinner()

        loading.update.assert_called_once_with("B")
        assert loading.idx == 0

class TestBotMessage:
    """Тесты сообщения бота."""

    def test_init_with_text(self):
        """Инициализация с текстом."""
        msg = BotMessage("Hello")
        assert msg.raw_text == "Hello"

    def test_init_empty(self):
        """Инициализация без текста."""
        msg = BotMessage()
        assert msg.raw_text == ""

    def test_compose(self):
        """Компоновка содержит spinner и bubble."""
        msg = BotMessage()
        children = list(msg.compose())

        assert len(children) == 2
        assert isinstance(children[0], BotLoading)
        assert isinstance(children[1], Static)

    def test_on_mount_with_text(self):
        """При монтировании с текстом скрывается спиннер."""
        msg = BotMessage("Response")
        msg.spinner = MagicMock()
        msg.bubble = MagicMock()

        msg.on_mount()

        assert msg.spinner.display is False
        assert msg.bubble.display is True

    def test_on_mount_without_text(self):
        """При монтировании без текста показывается спиннер."""
        msg = BotMessage()
        msg.spinner = MagicMock()
        msg.bubble = MagicMock()

        msg.on_mount()

        assert msg.bubble.display is False

    def test_update_content(self):
        """Обновление содержимого."""
        msg = BotMessage()
        msg.spinner = MagicMock()
        msg.spinner.display = True
        msg.bubble = MagicMock()

        msg.update_content("New text")

        assert msg.spinner.display is False
        assert msg.bubble.display is True
        assert msg.raw_text == "New text"
        msg.bubble.update.assert_called_once()

    def test_update_content_with_markdown(self):
        """Обновление с Markdown."""
        msg = BotMessage()
        msg.spinner = MagicMock()
        msg.bubble = MagicMock()

        msg.update_content("**bold**")

        call_args = msg.bubble.update.call_args[0][0]
        assert isinstance(call_args, RichMarkdown)

class TestChatLog:
    """Тесты лога чата."""

    def test_init(self):
        """Инициализация."""
        log = ChatLog(id="chat_log")
        assert log.id == "chat_log"

    def test_append_user_message(self):
        """Добавление сообщения пользователя."""
        log = ChatLog()
        log.mount = MagicMock()
        log.scroll_end = MagicMock()

        with patch("tui.widgets.chat_log.UserMessage") as mock_user_msg:
            mock_widget = MagicMock()
            mock_user_msg.return_value = mock_widget

            result = log.append_message("Hello", is_user=True)

        mock_user_msg.assert_called_once_with("Hello")
        log.mount.assert_called_once_with(mock_widget)
        log.scroll_end.assert_called_once_with(animate=False)
        assert result == mock_widget

    def test_append_bot_message(self):
        """Добавление сообщения бота."""
        log = ChatLog()
        log.mount = MagicMock()
        log.scroll_end = MagicMock()

        with patch("tui.widgets.chat_log.BotMessage") as mock_bot_msg:
            mock_widget = MagicMock()
            mock_bot_msg.return_value = mock_widget

            result = log.append_message("Response", is_user=False)

        mock_bot_msg.assert_called_once_with("Response")
        assert result == mock_widget

class TestChatItem:
    """Тесты элемента чата в списке."""

    def test_init(self):
        """Инициализация."""
        item = ChatItem(chat_id=5, title="Test Chat", is_active=True)
        assert item.chat_id == 5
        assert item.chat_title == "Test Chat"
        assert item.is_active is True
        assert item.id == "chat_item_5"

    def test_init_not_active(self):
        """Инициализация неактивного."""
        item = ChatItem(chat_id=1, title="Chat")
        assert item.is_active is False

    def test_compose(self):
        """Компоновка содержит кнопки и input."""
        item = ChatItem(chat_id=1, title="Chat")
        children = list(item.compose())
        assert len(children) == 1

    def test_edit_name(self):
        """Перевод в режим редактирования."""
        item = ChatItem(chat_id=1, title="Chat")
        mock_btn_select = MagicMock()
        mock_btn_rename = MagicMock()
        mock_input = MagicMock()

        def mock_query_one(selector):
            if selector == "#btn_select":
                return mock_btn_select
            elif selector == "#btn_rename":
                return mock_btn_rename
            elif selector == "#input_rename":
                return mock_input

        item.query_one = mock_query_one

        item.edit_name()

        assert mock_btn_select.styles.display == "none"
        assert mock_btn_rename.styles.display == "none"
        assert mock_input.styles.display == "block"
        mock_input.focus.assert_called_once()

    def test_on_button_pressed_select(self):
        """Нажатие кнопки выбора чата."""
        item = ChatItem(chat_id=3, title="Chat")
        item.app = MagicMock()
        item.screen = MagicMock()

        mock_button = MagicMock()
        mock_button.id = "btn_select"

        event = MagicMock()
        event.button = mock_button

        item.on_button_pressed(event)

        item.screen.switch_to_chat.assert_called_once_with(3)

    def test_on_button_pressed_rename(self):
        """Нажатие кнопки переименования."""
        item = ChatItem(chat_id=1, title="Chat")
        item.edit_name = MagicMock()

        mock_button = MagicMock()
        mock_button.id = "btn_rename"

        event = MagicMock()
        event.button = mock_button

        item.on_button_pressed(event)

        item.edit_name.assert_called_once()

    def test_on_button_pressed_delete(self):
        """Нажатие кнопки удаления."""
        item = ChatItem(chat_id=2, title="Chat")
        item.app = MagicMock()

        mock_button = MagicMock()
        mock_button.id = "btn_delete"

        event = MagicMock()
        event.button = mock_button

        item.on_button_pressed(event)

        item.app.chat_manager.delete_chat.assert_called_once_with(
            item.app, item.screen, item
        )

    def test_on_input_submitted_rename(self):
        """Подтверждение переименования."""
        item = ChatItem(chat_id=1, title="Old")
        item.app = MagicMock()

        mock_input = MagicMock()
        mock_input.id = "input_rename"

        event = MagicMock()
        event.input = mock_input
        event.value = "New Title"

        mock_btn_select = MagicMock()
        mock_btn_rename = MagicMock()
        mock_input_rename = MagicMock()

        def mock_query_one(selector):
            mapping = {
                "#btn_select": mock_btn_select,
                "#btn_rename": mock_btn_rename,
                "#input_rename": mock_input_rename,
            }
            return mapping[selector]

        item.query_one = mock_query_one

        item.on_input_submitted(event)

        item.app.chat_manager.rename_chat.assert_called_once_with(
            item.app, item, "New Title"
        )
        assert mock_btn_select.styles.display == "block"
        assert mock_btn_rename.styles.display == "block"
        assert mock_input_rename.styles.display == "none"

    def test_on_input_submitted_empty(self):
        """Пустое название — отмена переименования."""
        item = ChatItem(chat_id=1, title="Old")
        item.app = MagicMock()

        mock_input = MagicMock()
        mock_input.id = "input_rename"

        event = MagicMock()
        event.input = mock_input
        event.value = "   "

        mock_btn_select = MagicMock()
        mock_btn_rename = MagicMock()
        mock_input_rename = MagicMock()

        def mock_query_one(selector):
            mapping = {
                "#btn_select": mock_btn_select,
                "#btn_rename": mock_btn_rename,
                "#input_rename": mock_input_rename,
            }
            return mapping[selector]

        item.query_one = mock_query_one

        item.on_input_submitted(event)

        item.app.chat_manager.rename_chat.assert_not_called()
