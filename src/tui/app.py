from textual.app import App, ComposeResult
from widgets.header import AppHeader
from screens.chat import ChatScreen

class G4Free_TUI(App):

    CSS_PATH = "styles/app_style.tcss"

    def compose(self) -> ComposeResult:
        yield AppHeader()

    def on_mount(self):
        self.push_screen(ChatScreen())

if __name__ == "__main__":
    app = G4Free_TUI()
    app.run()