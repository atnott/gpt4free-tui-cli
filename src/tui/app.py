from textual.app import App, ComposeResult
from widgets.header import AppHeader

class G4Free_TUI(App):

    CSS_PATH = "styles/app_style.tcss"

    def compose(self) -> ComposeResult:
        yield AppHeader()

if __name__ == "__main__":
    app = G4Free_TUI()
    app.run()