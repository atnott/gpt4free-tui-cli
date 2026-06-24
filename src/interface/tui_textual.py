from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll, HorizontalGroup
from textual.widgets import Placeholder, RichLog, Input, Header, Footer


class ExperementalTUI(App):
    CSS_PATH = "styles/tui_styles.tcss"

    def compose(self) -> ComposeResult:
        yield Header(id = "TUI_header")
        yield Horizontal(
            Placeholder(id = "Models_window"),
            Placeholder(id= "Chat_window"),
            Placeholder(id = "Providers_window"),
            id = "Main_container"
        )
        yield Footer(id = "TUI_footer")


if __name__ == "__main__":
    app = ExperementalTUI()
    app.run()
