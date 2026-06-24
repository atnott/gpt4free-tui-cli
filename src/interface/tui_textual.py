from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll, HorizontalGroup
from textual.widgets import Placeholder, RichLog, Input, Header, Footer


class ExperementalTUI(App):
    CSS_PATH = "styles/tui_styles.tcss"

    def compose(self) -> ComposeResult:
        yield Header(id = "TUI_header")
        yield Horizontal(
            Placeholder(id = "Models_window"),
            Container(
                RichLog(id = "chat_log"),
                Input(placeholder = "Input your text here...", id = "user_input"),
                id = "Chat_window"
            ),
            Placeholder(id = "Providers_window"),
            id = "Main_container"
        )
        yield Footer(id = "TUI_footer")

    def on_mount(self) -> None:
        self.theme = "textual-dark"
        
        self.query_one("#Chat_window").border_title = "Chat"


    #Ввод пользователя
    def on_input_submitted(self, event: Input.Submitted) -> None:
        user_text = event.value.strip()

        if not user_text:
            return

        chat_log = self.query_one("#chat_log", RichLog)
        chat_log.write(f"User: {user_text}")
        event.input.value = ""


if __name__ == "__main__":
    app = ExperementalTUI()
    app.run()
