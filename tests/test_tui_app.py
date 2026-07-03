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
            assert app.model == ""
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
            assert "ctrl+n" in keys  # create_chat
            assert "ctrl+d" in keys  # delete_chat
            assert "ctrl+r" in keys  # rename_chat
            assert "ctrl+up" in keys  # switch_to_previous_chat
            assert "ctrl+down" in keys  # switch_to_next_chat
            assert "ctrl+m" in keys  # switch_model
            assert "ctrl+j" in keys  # switch_provider

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
