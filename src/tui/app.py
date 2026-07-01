from textual.app import App, ComposeResult
from core.config import ConfigManager
from core.engine import G4FEngine
from tui.screens.chat import ChatScreen
from tui.widgets.header import AppHeader

class G4FreeTUI(App):
    CSS_PATH = "styles/app_style.tcss"
    DEFAULT_MODEL = "gpt-4o"
    DEFAULT_THEME = "gruvbox"
    App.theme = DEFAULT_THEME

    def __init__(self) -> None:
        super().__init__()

        self.engine = G4FEngine()
        self.config = ConfigManager()

        settings = self.config.load_config() or {}

        self.model = settings.get("last_model", self.DEFAULT_MODEL)
        self.provider = settings.get("last_provider")

    def compose(self) -> ComposeResult:
        yield AppHeader()

    def on_mount(self) -> None:
        self.push_screen(ChatScreen())

if __name__ == "__main__":
    G4FreeTUI().run()