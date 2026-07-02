from textual.containers import Horizontal, Vertical
from textual.widgets import Label

class AppHeader(Horizontal):

    def __init__(self, id=None):
        super().__init__(id=id)

    def compose(self):        
        with Vertical(id = "header_left"):
            yield Label("G4Free TUI", id="name")
            yield Label("Select in multiple chats", id = "desc")

        with Vertical(id = "header_mid"):
            yield Label("", id="header_chat_title")
            yield Label("", id="header_model")

        yield Label("Choose your model\nand provider", id = "header_right")

    def on_mount(self) -> None:
        """Вызывается, когда хедер появляется на экране."""
        self.watch(self.app, "model", self.update_model_label)
        self.watch(self.app, "current_chat_title", self.update_chat_title)

    def update_model_label(self, new_model_name: str) -> None:
        """Автоматически обновляет текст в хедере."""
        try:
            label = self.query_one("#header_model", Label)
            label.update(f"{new_model_name.upper()}")
        except Exception:
            pass

    def update_chat_title(self, new_title: str) -> None:
        """Вызывается автоматически при смене или переименовании чата"""
        try:
            self.query_one("#header_chat_title", Label).update(f"{new_title}")
        except Exception:
            pass