import pytest
from unittest.mock import MagicMock, patch, PropertyMock, AsyncMock

from textual.app import App
from textual._context import active_app
from textual.widgets import Static, Input, Button, Select
from textual.widgets.option_list import Option
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

@pytest.fixture
def app_context():
    """Создаёт Textual App с активным контекстом и нужными атрибутами."""
    app = App()
    app._compose_stacks = [[], [], []]
    app._composed = [[]]
    app.model = "gpt-4o"
    app.provider = None
    app.current_chat_id = 1
    app.current_chat_title = ""
    app.config = MagicMock()
    app.db = MagicMock()
    app.engine = MagicMock()
    app.chat_manager = MagicMock()
    app.DEFAULT_MODEL = "gpt-4o"
    app.MAX_CONTEXT = 20
    token = active_app.set(app)
    try:
        yield app
    finally:
        active_app.reset(token)

@pytest.fixture
def mock_screen():
    """Мок screen для тестов, где нужен self.screen."""
    screen = MagicMock()
    screen.query_one.return_value = MagicMock()
    screen.query.return_value = []
    screen.switch_to_chat = MagicMock()
    return screen

class TestAppHeader:
    """Тесты хедера."""

    def test_compose_structure(self, app_context):
        """Структура компоновки."""
        header = AppHeader(id="Header")
        header._app = app_context
        children = list(header.compose())
        assert len(children) == 5

    def test_on_mount_watches_model(self, app_context):
        """Подписка на изменение model."""
        header = AppHeader()
        header._app = app_context
        with patch.object(header, "watch") as mock_watch:
            header.on_mount()
        mock_watch.assert_any_call(app_context, "model", header.update_model_label)

    def test_on_mount_watches_chat_title(self, app_context):
        """Подписка на изменение current_chat_title."""
        header = AppHeader()
        header._app = app_context
        with patch.object(header, "watch") as mock_watch:
            header.on_mount()
        mock_watch.assert_any_call(app_context, "current_chat_title", header.update_chat_title)

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
        assert "Test message" in str(children[0].render())

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
        msg.on_mount()
        assert msg.spinner.display is False
        assert msg.bubble.display is True

    def test_on_mount_without_text(self):
        """При монтировании без текста показывается спиннер."""
        msg = BotMessage()
        msg.on_mount()
        assert msg.bubble.display is False

    def test_update_content(self):
        """Обновление содержимого."""
        msg = BotMessage()
        msg.on_mount()
        msg.update_content("New text")
        assert msg.spinner.display is False
        assert msg.bubble.display is True
        assert msg.raw_text == "New text"

    def test_update_content_with_markdown(self):
        """Обновление с Markdown."""
        msg = BotMessage()
        msg.on_mount()
        msg.update_content("**bold**")
        assert msg.raw_text == "**bold**"

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

    def test_compose(self, app_context, mock_screen):
        """Компоновка содержит кнопки и input."""
        item = ChatItem(chat_id=1, title="Chat")
        item._app = app_context
        with patch.object(App, "screen", new_callable=PropertyMock) as mock_app_screen:
            mock_app_screen.return_value = mock_screen
            children = list(item.compose())
        assert len(children) == 4

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

    def test_on_button_pressed_select(self, app_context, mock_screen):
        """Нажатие кнопки выбора чата."""
        item = ChatItem(chat_id=3, title="Chat")
        item._app = app_context
        with patch("textual.dom.DOMNode.screen", new_callable=PropertyMock) as mock_screen_prop:
            mock_screen_prop.return_value = mock_screen
            mock_button = MagicMock()
            mock_button.id = "btn_select"
            event = MagicMock()
            event.button = mock_button
            item.on_button_pressed(event)
            mock_screen.switch_to_chat.assert_called_once_with(3)

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

    def test_on_button_pressed_delete(self, app_context, mock_screen):
        """Нажатие кнопки удаления."""
        item = ChatItem(chat_id=2, title="Chat")
        item._app = app_context
        with patch("textual.dom.DOMNode.screen", new_callable=PropertyMock) as mock_screen_prop:
            mock_screen_prop.return_value = mock_screen
            mock_button = MagicMock()
            mock_button.id = "btn_delete"
            event = MagicMock()
            event.button = mock_button
            item.on_button_pressed(event)
            app_context.chat_manager.delete_chat.assert_called_once_with(
                app_context, mock_screen, item
            )

    def test_on_input_submitted_rename(self, app_context):
        """Подтверждение переименования."""
        item = ChatItem(chat_id=1, title="Old")
        item._app = app_context
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
        app_context.chat_manager.rename_chat.assert_called_once_with(
            app_context, item, "New Title"
        )
        assert mock_btn_select.styles.display == "block"
        assert mock_btn_rename.styles.display == "block"
        assert mock_input_rename.styles.display == "none"

    def test_on_input_submitted_empty(self, app_context):
        """Пустое название — отмена переименования."""
        item = ChatItem(chat_id=1, title="Old")
        item._app = app_context
        mock_input = MagicMock()
        mock_input.id = "input_rename"
        event = MagicMock()
        event.input = mock_input
        event.value = " "
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
        app_context.chat_manager.rename_chat.assert_not_called()

class TestChatSidebar:
    """Тесты боковой панели чатов."""

    def test_compose(self, app_context):
        """Компоновка содержит кнопку и список."""
        sidebar = ChatSidebar()
        sidebar._app = app_context
        children = list(sidebar.compose())
        assert len(children) == 1

    def test_on_mount_loads_chats(self, app_context):
        """Загрузка чатов при монтировании."""
        sidebar = ChatSidebar()
        sidebar._app = app_context
        app_context.current_chat_id = 1
        app_context.db.get_all_chats.return_value = [
            {"id": 1, "title": "Chat 1"},
            {"id": 2, "title": "Chat 2"},
        ]
        mock_chat_list = MagicMock()
        sidebar.query_one = MagicMock(return_value=mock_chat_list)
        with patch("tui.widgets.chats_sidebar.ChatItem") as mock_item_class:
            mock_items = [MagicMock(), MagicMock()]
            mock_item_class.side_effect = mock_items
            sidebar.on_mount()
            assert mock_item_class.call_count == 2
            mock_chat_list.mount.assert_called()

    def test_on_button_pressed_create_chat(self, app_context, mock_screen):
        """Создание чата по кнопке."""
        sidebar = ChatSidebar()
        sidebar._app = app_context
        with patch("textual.dom.DOMNode.screen", new_callable=PropertyMock) as mock_screen_prop:
            mock_screen_prop.return_value = mock_screen
            app_context.db.create_chat.return_value = 5
            mock_chat_list = MagicMock()
            sidebar.query_one = MagicMock(return_value=mock_chat_list)
            mock_button = MagicMock()
            mock_button.id = "btn_create_chat"
            event = MagicMock()
            event.button = mock_button
            with patch("tui.widgets.chats_sidebar.ChatItem") as mock_item_class:
                mock_item = MagicMock()
                mock_item_class.return_value = mock_item
                sidebar.on_button_pressed(event)
                app_context.db.create_chat.assert_called_once_with("New chat")
                mock_chat_list.mount.assert_called_once_with(mock_item)
                mock_item.scroll_visible.assert_called_once()
                mock_screen.switch_to_chat.assert_called_once_with(5)

class TestChoosePanel:
    """Тесты панели выбора модели/провайдера."""

    def test_compose_with_models(self, app_context):
        """Компоновка с доступными моделями."""
        panel = ChoosePanel()
        panel._app = app_context
        app_context.engine.get_all_models.return_value = ["gpt-4o", "claude-3"]
        app_context.model = "gpt-4o"
        children = list(panel.compose())
        assert len(children) == 3

    def test_compose_fallback_model(self, app_context):
        """Выбор fallback модели."""
        panel = ChoosePanel()
        panel._app = app_context
        app_context.engine.get_all_models.return_value = ["gpt-4o", "claude-3"]
        app_context.model = "nonexistent"
        app_context.DEFAULT_MODEL = "gpt-4o"
        list(panel.compose())
        assert app_context.model == "gpt-4o"

    def test_on_mount_loads_providers(self, app_context):
        """Загрузка провайдеров при монтировании."""
        panel = ChoosePanel()
        panel._app = app_context
        app_context.model = "gpt-4o"
        mock_provider = MagicMock()
        mock_provider.name = "ProviderA"
        mock_provider.supported_models = ["gpt-4o"]
        app_context.engine.get_available_providers.return_value = [mock_provider]
        panel.load_providers = MagicMock(return_value=["ProviderA"])
        panel.on_mount()
        panel.load_providers.assert_called_once_with("gpt-4o")

    def test_load_providers(self, app_context):
        """Загрузка провайдеров для модели."""
        panel = ChoosePanel()
        panel._app = app_context
        app_context.model = "gpt-4o"
        mock_provider1 = MagicMock()
        mock_provider1.name = "ProviderA"
        mock_provider1.supported_models = ["gpt-4o", "claude-3"]
        mock_provider2 = MagicMock()
        mock_provider2.name = "ProviderB"
        mock_provider2.supported_models = ["claude-3"]
        app_context.engine.get_available_providers.return_value = [mock_provider1, mock_provider2]
        mock_option_list = MagicMock()
        panel.query_one = MagicMock(return_value=mock_option_list)
        result = panel.load_providers("gpt-4o")
        assert result == ["ProviderA"]
        mock_option_list.clear_options.assert_called_once()
        assert mock_option_list.add_option.call_count == 2

    def test_on_select_changed_updates_model(self, app_context):
        """Изменение выбора модели."""
        panel = ChoosePanel()
        panel._app = app_context
        app_context.model = "gpt-4o"
        panel.load_providers = MagicMock(return_value=["ProviderA"])
        mock_event = MagicMock()
        mock_event.select.id = "model"
        mock_event.value = "claude-3"
        panel.on_select_changed(mock_event)
        assert app_context.model == "claude-3"
        app_context.config.update_config.assert_called_once()

    def test_on_select_changed_blank(self, app_context):
        """Пустой выбор — игнорируется."""
        panel = ChoosePanel()
        panel._app = app_context
        mock_event = MagicMock()
        mock_event.select.id = "model"
        mock_event.value = Select.BLANK
        panel.on_select_changed(mock_event)
        app_context.config.update_config.assert_not_called()

    def test_on_option_list_option_selected_auto(self, app_context):
        """Выбор Auto провайдера."""
        panel = ChoosePanel()
        panel._app = app_context
        mock_event = MagicMock()
        mock_event.option.prompt = "Auto"
        panel.on_option_list_option_selected(mock_event)
        assert app_context.provider is None
        app_context.config.update_config.assert_called_once()

    def test_on_option_list_option_selected_provider(self, app_context):
        """Выбор конкретного провайдера."""
        panel = ChoosePanel()
        panel._app = app_context
        mock_event = MagicMock()
        mock_event.option.prompt = "Bing"
        panel.on_option_list_option_selected(mock_event)
        assert app_context.provider == "Bing"

class TestChatInput:
    """Тесты поля ввода."""

    def test_init(self):
        """Инициализация с placeholder."""
        inp = ChatInput(id="chat_input")
        assert inp.id == "chat_input"
        assert "Input your request" in inp.placeholder

    @pytest.mark.asyncio
    async def test_on_input_submitted_empty(self, app_context):
        """Пустой ввод — игнорируется."""
        inp = ChatInput()
        inp._app = app_context
        mock_event = MagicMock()
        mock_event.value = " "
        await inp.on_input_submitted(mock_event)

    @pytest.mark.asyncio
    async def test_on_input_submitted_success(self, app_context, mock_screen):
        """Успешная отправка сообщения."""
        inp = ChatInput()
        inp._app = app_context
        with patch("textual.dom.DOMNode.screen", new_callable=PropertyMock) as mock_screen_prop:
            mock_screen_prop.return_value = mock_screen
            app_context.model = "gpt-4o"
            app_context.provider = None

            async def mock_stream(*args, **kwargs):
                yield "Hello"
                yield " world"

            app_context.engine.get_chat_stream.return_value = mock_stream()

            await inp.on_input_submitted(MagicMock(value="Hello"))

            assert inp.value == ""
            mock_screen.query_one.return_value.append_message.assert_any_call("Hello", is_user=True)
            mock_screen.query_one.return_value.append_message.assert_any_call("", is_user=False)

    @pytest.mark.asyncio
    async def test_on_input_submitted_error(self, app_context, mock_screen):
        """Обработка ошибки движка."""
        inp = ChatInput()
        inp._app = app_context
        with patch("textual.dom.DOMNode.screen", new_callable=PropertyMock) as mock_screen_prop:
            mock_screen_prop.return_value = mock_screen
            app_context.model = "gpt-4o"

            async def mock_stream(*args, **kwargs):
                raise Exception("Engine error")
                yield ""

            app_context.engine.get_chat_stream.return_value = mock_stream()

            await inp.on_input_submitted(MagicMock(value="Test"))

            bot_msg = mock_screen.query_one.return_value.append_message.return_value
            assert bot_msg.update_content.called