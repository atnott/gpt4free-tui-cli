from textual.app import App, ComposeResult
from textual.widgets import Input
from textual.reactive import reactive
from core.config import ConfigManager
from core.engine import G4FEngine
from core.database import DatabaseManager
from tui.tui_core.chat_manager import ChatManager
from tui.screens.chat import ChatScreen
from tui.widgets.header import AppHeader

class G4FreeTUI(App):
    CSS_PATH = "styles/app_style.tcss"
    MAX_CONTEXT = 20

    BINDINGS = [
        ("ctrl+n", "create_chat", "Create chat"),
        ("ctrl+d", "delete_chat", "Delete current chat"),
        ("ctrl+r", "rename_chat", "Rename current chat"),
    ]

    model = reactive("")
    current_chat_title = reactive("")

    def __init__(self) -> None:
        super().__init__()

        self.engine = G4FEngine()
        self.config = ConfigManager()
        self.db = DatabaseManager()
        self.chat_manager = ChatManager()

        settings = self.config.load_config() or {}

        self.model = settings.get("last_model")
        self.provider = settings.get("last_provider")
        self.current_chat_id = settings.get("current_chat_id")

    def compose(self) -> ComposeResult:
        yield AppHeader()

    def on_mount(self) -> None:
        self.push_screen(ChatScreen())

    def on_unmount(self) -> None:
        """Вызывается автоматически при выходе из приложения"""
        try:
            self.config.update_config(
                last_model=self.model,
                last_provider=self.provider,
                current_chat_id=self.current_chat_id
            )
        except Exception as e:
            print(f"Не удалось сохранить конфигурацию: {e}")

    def on_key(self, event) -> None:
        if event.key == "space":
            if not isinstance(self.focused, Input):
                event.prevent_default()
                event.stop()
                
                try:
                    self.screen.query_one("#chat_input").focus()
                except Exception:
                    pass

    def action_create_chat(self) -> None:
        """Создание нового чата (Ctrl+N)"""
        self.chat_manager.create_new_chat(app=self, screen=self.screen)

    def action_delete_chat(self) -> None:
        """Удаление текущего активного чата (Ctrl+D)"""
        if self.current_chat_id is not None:
            try:
                current_item = self.screen.query_one(f"#chat_item_{self.current_chat_id}") 
                self.chat_manager.delete_chat(app=self, screen=self.screen, chat_item=current_item)
            except Exception:
                pass

    def action_rename_chat(self) -> None:
        """Переименование текущего активного чата (Ctrl+R)"""
        if self.current_chat_id is not None:
            try:
                current_item = self.screen.query_one(f"#chat_item_{self.current_chat_id}") 
                current_item.edit_name()
            except Exception:
                pass

if __name__ == "__main__":
    G4FreeTUI().run()