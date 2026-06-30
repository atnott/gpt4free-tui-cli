from textual.app import App, ComposeResult
from tui.widgets.header import AppHeader
from tui.screens.chat import ChatScreen
from core.engine import G4FEngine
from core.config import ConfigManager

class G4Free_TUI(App):

    def __init__(self):
        super().__init__()
        self.engine = G4FEngine()
        self.config = ConfigManager()
        
        settings = self.config.load_settings()
        self.model = settings["last_model"] if settings else "gpt-4o"
        self.provider = settings.get("last_provider") if settings else None

    def compose(self) -> ComposeResult:
        yield AppHeader()

    def on_mount(self):
        self.push_screen(ChatScreen())

if __name__ == "__main__":
    app = G4Free_TUI()
    app.run()