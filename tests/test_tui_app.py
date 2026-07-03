import pytest
from unittest.mock import patch, MagicMock, PropertyMock

from textual.widgets import Input

from tui.app import G4FreeTUI


class TestG4FreeTUIInitialization:
    """Тесты инициализации приложения."""

    @patch("tui.app.G4FEngine")
    @patch("tui.app.ConfigManager")
    @patch("tui.app.DatabaseManager")
    @patch("tui.app.ChatManager")
    def test_init_creates_dependencies(self, mock_chat_mgr, mock_db, mock_config, mock_engine):
        """Проверка создания зависимостей при инициализации."""
        with patch.object(G4FreeTUI, "push_screen"):
            app = G4FreeTUI()
            assert app.engine is not None
            assert app.config is not None
            assert app.db is not None
            assert app.chat_manager is not None

    @patch("tui.app.G4FEngine")
    @patch("tui.app.ConfigManager")
    @patch("tui.app.DatabaseManager")
    @patch("tui.app.ChatManager")
    def test_init_loads_settings(self, mock_chat_mgr, mock_db, mock_config, mock_engine):
        """Загрузка настроек из конфига."""
        mock_config_instance = MagicMock()
        mock_config_instance.load_config.return_value = {
            "last_model": "claude-3",
            "last_provider": "Bing",
            "current_chat_id": 5
        }
        mock_config.return_value = mock_config_instance

        with patch.object(G4FreeTUI, "push_screen"):
            app = G4FreeTUI()
            assert app.model == "claude-3"
            assert app.provider == "Bing"
            assert app.current_chat_id == 5

    @patch("tui.app.G4FEngine")
    @patch("tui.app.ConfigManager")
    @patch("tui.app.DatabaseManager")
    @patch("tui.app.ChatManager")
    def test_init_empty_config(self, mock_chat_mgr, mock_db, mock_config, mock_engine):
        """Обработка пустого конфига."""
        mock_config_instance = MagicMock()
        mock_config_instance.load_config.return_value = {}
        mock_config.return_value = mock_config_instance

        with patch.object(G4FreeTUI, "push_screen"):
            app = G4FreeTUI()
            assert app.model is None
            assert app.provider is None
            assert app.current_chat_id is None

    @patch("tui.app.G4FEngine")
    @patch("tui.app.ConfigManager")
    @patch("tui.app.DatabaseManager")
    @patch("tui.app.ChatManager")
    def test_css_path_set(self, mock_chat_mgr, mock_db, mock_config, mock_engine):
        """Путь к CSS-файлу."""
        with patch.object(G4FreeTUI, "push_screen"):
            app = G4FreeTUI()
            assert app.CSS_PATH == "styles/app_style.tcss"

    @patch("tui.app.G4FEngine")
    @patch("tui.app.ConfigManager")
    @patch("tui.app.DatabaseManager")
    @patch("tui.app.ChatManager")
    def test_max_context_constant(self, mock_chat_mgr, mock_db, mock_config, mock_engine):
        """Константа MAX_CONTEXT."""
        with patch.object(G4FreeTUI, "push_screen"):
            app = G4FreeTUI()
            assert app.MAX_CONTEXT == 20

    @patch("tui.app.G4FEngine")
    @patch("tui.app.ConfigManager")
    @patch("tui.app.DatabaseManager")
    @patch("tui.app.ChatManager")
    def test_bindings_defined(self, mock_chat_mgr, mock_db, mock_config, mock_engine):
        """Проверка наличия всех горячих клавиш."""
        with patch.object(G4FreeTUI, "push_screen"):
            app = G4FreeTUI()
            bindings = app.BINDINGS

            keys = [b[0] for b in bindings]
            assert "ctrl+n" in keys
            assert "ctrl+d" in keys
            assert "ctrl+r" in keys
            assert "ctrl+up" in keys
            assert "ctrl+down" in keys
            assert "ctrl+m" in keys
            assert "ctrl+j" in keys


class TestG4FreeTUICompose:
    """Тесты compose() — построение UI."""

    @patch("tui.app.G4FEngine")
    @patch("tui.app.ConfigManager")
    @patch("tui.app.DatabaseManager")
    @patch("tui.app.ChatManager")
    def test_compose_yields_header(self, mock_chat_mgr, mock_db, mock_config, mock_engine):
        """Compose должен содержать AppHeader."""
        with patch.object(G4FreeTUI, "push_screen"):
            app = G4FreeTUI()

        with patch("tui.app.AppHeader"):
            list(app.compose())


class TestG4FreeTUIMount:
    """Тесты on_mount."""

    @patch("tui.app.G4FEngine")
    @patch("tui.app.ConfigManager")
    @patch("tui.app.DatabaseManager")
    @patch("tui.app.ChatManager")
    def test_on_mount_pushes_chat_screen(self, mock_chat_mgr, mock_db, mock_config, mock_engine):
        """При монтировании открывается ChatScreen."""
        with patch.object(G4FreeTUI, "push_screen") as mock_push:
            app = G4FreeTUI()
            app.on_mount()
            mock_push.assert_called_once()

class TestG4FreeTUIUnmount:
    """Тесты on_unmount — сохранение конфига."""

    @patch("tui.app.G4FEngine")
    @patch("tui.app.ConfigManager")
    @patch("tui.app.DatabaseManager")
    @patch("tui.app.ChatManager")
    def test_on_unmount_saves_config(self, mock_chat_mgr, mock_db, mock_config, mock_engine):
        """Сохранение конфига при выходе."""
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance

        with patch.object(G4FreeTUI, "push_screen"):
            app = G4FreeTUI()
            app.model = "gpt-4o-mini"
            app.provider = "OpenaiChat"
            app.current_chat_id = 3
            app.on_unmount()

        mock_config_instance.update_config.assert_called_once_with(
            last_model="gpt-4o-mini",
            last_provider="OpenaiChat",
            current_chat_id=3
        )

    @patch("tui.app.G4FEngine")
    @patch("tui.app.ConfigManager")
    @patch("tui.app.DatabaseManager")
    @patch("tui.app.ChatManager")
    def test_on_unmount_handles_error(self, mock_chat_mgr, mock_db, mock_config, mock_engine):
        """Обработка ошибки при сохранении конфига."""
        mock_config_instance = MagicMock()
        mock_config_instance.update_config.side_effect = Exception("Disk full")
        mock_config.return_value = mock_config_instance

        with patch.object(G4FreeTUI, "push_screen"):
            app = G4FreeTUI()
            app.on_unmount()

class TestG4FreeTUIOnKey:
    """Тесты обработки клавиш."""
    @patch("tui.app.G4FEngine")
    @patch("tui.app.ConfigManager")
    @patch("tui.app.DatabaseManager")
    @patch("tui.app.ChatManager")
    def test_space_in_input_no_action(self, mock_chat_mgr, mock_db, mock_config, mock_engine):
        """Пробел в input не вызывает prevent_default."""
        with patch.object(G4FreeTUI, "push_screen"):
            app = G4FreeTUI()

        mock_event = MagicMock()
        mock_event.key = "space"

        with patch.object(type(app), "focused", new_callable=PropertyMock) as mock_focused:
            mock_focused.return_value = MagicMock(spec=Input)
            app.on_key(mock_event)

        mock_event.prevent_default.assert_not_called()


class TestG4FreeTUIActions:
    """Тесты action_* методов."""

    @patch("tui.app.G4FEngine")
    @patch("tui.app.ConfigManager")
    @patch("tui.app.DatabaseManager")
    @patch("tui.app.ChatManager")
    def test_action_create_chat(self, mock_chat_mgr, mock_db, mock_config, mock_engine):
        """Создание чата через action."""
        mock_chat_manager = MagicMock()
        mock_chat_mgr.return_value = mock_chat_manager

        with patch.object(G4FreeTUI, "push_screen"):
            app = G4FreeTUI()

        mock_screen = MagicMock()
        with patch.object(type(app), "screen", new_callable=PropertyMock) as mock_screen_prop:
            mock_screen_prop.return_value = mock_screen
            app.action_create_chat()

        mock_chat_manager.create_new_chat.assert_called_once_with(
            app=app, screen=mock_screen
        )

    @patch("tui.app.G4FEngine")
    @patch("tui.app.ConfigManager")
    @patch("tui.app.DatabaseManager")
    @patch("tui.app.ChatManager")
    def test_action_delete_chat_with_current(self, mock_chat_mgr, mock_db, mock_config, mock_engine):
        """Удаление текущего чата."""
        mock_chat_manager = MagicMock()
        mock_chat_mgr.return_value = mock_chat_manager

        with patch.object(G4FreeTUI, "push_screen"):
            app = G4FreeTUI()
            app.current_chat_id = 5

        mock_screen = MagicMock()
        mock_item = MagicMock()
        mock_screen.query_one.return_value = mock_item

        with patch.object(type(app), "screen", new_callable=PropertyMock) as mock_screen_prop:
            mock_screen_prop.return_value = mock_screen
            app.action_delete_chat()

        mock_chat_manager.delete_chat.assert_called_once_with(
            app=app, screen=mock_screen, chat_item=mock_item
        )

    @patch("tui.app.G4FEngine")
    @patch("tui.app.ConfigManager")
    @patch("tui.app.DatabaseManager")
    @patch("tui.app.ChatManager")
    def test_action_delete_chat_no_current(self, mock_chat_mgr, mock_db, mock_config, mock_engine):
        """Удаление без текущего chat_id — ничего не делает."""
        with patch.object(G4FreeTUI, "push_screen"):
            app = G4FreeTUI()
            app.current_chat_id = None
            app.action_delete_chat()

    @patch("tui.app.G4FEngine")
    @patch("tui.app.ConfigManager")
    @patch("tui.app.DatabaseManager")
    @patch("tui.app.ChatManager")
    def test_action_rename_chat(self, mock_chat_mgr, mock_db, mock_config, mock_engine):
        """Переименование чата."""
        with patch.object(G4FreeTUI, "push_screen"):
            app = G4FreeTUI()
            app.current_chat_id = 3

        mock_screen = MagicMock()
        mock_item = MagicMock()
        mock_screen.query_one.return_value = mock_item

        with patch.object(type(app), "screen", new_callable=PropertyMock) as mock_screen_prop:
            mock_screen_prop.return_value = mock_screen
            app.action_rename_chat()

        mock_item.edit_name.assert_called_once()

    @patch("tui.app.G4FEngine")
    @patch("tui.app.ConfigManager")
    @patch("tui.app.DatabaseManager")
    @patch("tui.app.ChatManager")
    def test_action_switch_to_previous_chat(self, mock_chat_mgr, mock_db, mock_config, mock_engine):
        """Переключение на предыдущий чат."""
        mock_chat_manager = MagicMock()
        mock_chat_mgr.return_value = mock_chat_manager

        with patch.object(G4FreeTUI, "push_screen"):
            app = G4FreeTUI()

        mock_screen = MagicMock()
        with patch.object(type(app), "screen", new_callable=PropertyMock) as mock_screen_prop:
            mock_screen_prop.return_value = mock_screen
            app.action_switch_to_previous_chat()

        mock_chat_manager.switch_to_previous_chat.assert_called_once_with(
            app=app, screen=mock_screen
        )

    @patch("tui.app.G4FEngine")
    @patch("tui.app.ConfigManager")
    @patch("tui.app.DatabaseManager")
    @patch("tui.app.ChatManager")
    def test_action_switch_to_next_chat(self, mock_chat_mgr, mock_db, mock_config, mock_engine):
        """Переключение на следующий чат."""
        mock_chat_manager = MagicMock()
        mock_chat_mgr.return_value = mock_chat_manager

        with patch.object(G4FreeTUI, "push_screen"):
            app = G4FreeTUI()

        mock_screen = MagicMock()
        with patch.object(type(app), "screen", new_callable=PropertyMock) as mock_screen_prop:
            mock_screen_prop.return_value = mock_screen
            app.action_switch_to_next_chat()

        mock_chat_manager.switch_to_next_chat.assert_called_once_with(
            app=app, screen=mock_screen
        )

    @patch("tui.app.G4FEngine")
    @patch("tui.app.ConfigManager")
    @patch("tui.app.DatabaseManager")
    @patch("tui.app.ChatManager")
    def test_action_switch_model(self, mock_chat_mgr, mock_db, mock_config, mock_engine):
        """Фокус на выбор модели."""
        with patch.object(G4FreeTUI, "push_screen"):
            app = G4FreeTUI()

        mock_screen = MagicMock()
        mock_model_widget = MagicMock()
        mock_screen.query_one.return_value = mock_model_widget

        with patch.object(type(app), "screen", new_callable=PropertyMock) as mock_screen_prop:
            mock_screen_prop.return_value = mock_screen
            app.action_switch_model()

        mock_screen.query_one.assert_called_once_with("#model")
        mock_model_widget.focus.assert_called_once()

    @patch("tui.app.G4FEngine")
    @patch("tui.app.ConfigManager")
    @patch("tui.app.DatabaseManager")
    @patch("tui.app.ChatManager")
    def test_action_switch_provider(self, mock_chat_mgr, mock_db, mock_config, mock_engine):
        """Фокус на выбор провайдера."""
        with patch.object(G4FreeTUI, "push_screen"):
            app = G4FreeTUI()

        mock_screen = MagicMock()
        mock_provider_widget = MagicMock()
        mock_screen.query_one.return_value = mock_provider_widget

        with patch.object(type(app), "screen", new_callable=PropertyMock) as mock_screen_prop:
            mock_screen_prop.return_value = mock_screen
            app.action_switch_provider()

        mock_screen.query_one.assert_called_once_with("#providers")
        mock_provider_widget.focus.assert_called_once()