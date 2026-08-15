from textual.app import App, ComposeResult
from textual.widgets import Input
from textual.reactive import reactive
from gpt4free_tui_cli.bootstrap import ApplicationDependencies
from gpt4free_tui_cli.tui.screens.chat import ChatScreen
from gpt4free_tui_cli.tui.widgets.header import AppHeader
from pathlib import Path


class G4FreeTUI(App):
    # CSS_PATH = "styles/app_style.tcss"
    CSS_PATH = str(Path(__file__).parent / "styles" / "app_style.tcss")
    MAX_CONTEXT = 20

    BINDINGS = [
        ("ctrl+n", "create_chat", "Create chat"),
        ("ctrl+d", "delete_chat", "Delete current chat"),
        ("ctrl+r", "rename_chat", "Rename current chat"),
        ("ctrl+up", "switch_to_previous_chat", "Switch to previous chat"),
        ("ctrl+down", "switch_to_next_chat", "Switch to next chat"),
        ("ctrl+m", "switch_model", "Switch model"),
        ("ctrl+j", "switch_provider", "Switch provider"),
    ]

    model = reactive("")
    current_chat_title = reactive("")

    def __init__(self, dependencies: ApplicationDependencies) -> None:
        super().__init__()

        self.catalog = dependencies.catalog
        self.chat_service = dependencies.chat_service
        self.config = dependencies.config
        self.db = dependencies.db
        self.chat_manager = dependencies.chat_manager
        settings = self.config.load_config() or {}

        self.model = settings.get("last_model")
        self.provider = settings.get("last_provider")
        self.current_chat_id = self.resolve_chat_id(settings.get("current_chat_id"))

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
                current_chat_id=self.current_chat_id,
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

    def resolve_chat_id(self, saved_chat_id: int | None) -> int | None:
        """Проверяет, существует ли сохранённый чат в текущей БД; иначе берёт первый доступный"""
        all_chats = self.db.get_all_chats()
        valid_ids = {row["id"] for row in all_chats}

        if saved_chat_id in valid_ids:
            return saved_chat_id

        return all_chats[0]["id"] if all_chats else None

    def action_create_chat(self) -> None:
        """Создание нового чата (Ctrl+N)"""
        self.chat_manager.create_new_chat(app=self, screen=self.screen)

    def action_delete_chat(self) -> None:
        """Удаление текущего активного чата (Ctrl+D)"""
        if self.current_chat_id is not None:
            try:
                current_item = self.screen.query_one(
                    f"#chat_item_{self.current_chat_id}"
                )
                self.chat_manager.delete_chat(
                    app=self, screen=self.screen, chat_item=current_item
                )
            except Exception:
                pass

    def action_rename_chat(self) -> None:
        """Переименование текущего активного чата (Ctrl+R)"""
        if self.current_chat_id is not None:
            try:
                current_item = self.screen.query_one(
                    f"#chat_item_{self.current_chat_id}"
                )
                current_item.edit_name()
            except Exception:
                pass

    def action_switch_to_previous_chat(self) -> None:
        """Переключение на предыдущий чат (Ctrl+Up)"""
        self.chat_manager.switch_to_previous_chat(app=self, screen=self.screen)

    def action_switch_to_next_chat(self) -> None:
        """Переключение на следующий чат (Ctrl+Down)"""
        self.chat_manager.switch_to_next_chat(app=self, screen=self.screen)

    def action_switch_model(self) -> None:
        """Переключение модели (Ctrl+M)"""
        self.screen.query_one("#model").focus()

    def action_switch_provider(self) -> None:
        """Переключение провайдера (Ctrl+J)"""
        self.screen.query_one("#providers").focus()


if __name__ == "__main__":
    from gpt4free_tui_cli.bootstrap import create_application_dependencies

    G4FreeTUI(create_application_dependencies()).run()
