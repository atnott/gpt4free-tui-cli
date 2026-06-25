from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll, Vertical
from textual.widgets import Placeholder, Input, Header, Footer, Static
from datetime import datetime
from rich.markdown import Markdown


class ExperementalTUI(App):
    CSS_PATH = "styles/tui_styles.tcss"

    def compose(self) -> ComposeResult:
        yield Header(id = "TUI_header")
        yield Horizontal(
            Placeholder(id = "Models_window"),
            Container(
                VerticalScroll(id = "chat_log"),
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

        if event.input.id != "user_input":
            return
        
        user_text = event.value.strip()
        
        if not user_text:
            return

        chat_log = self.query_one("#chat_log", VerticalScroll)
        time_str = datetime.now().strftime("%H:%M")

        user_message = Vertical(
            Static(f"[dim][{time_str}][/dim] [bold]User:[/bold]"),
            Static(Markdown(user_text)),
            classes = "chat-message user-message"
        )
        chat_log.mount(user_message)

        ## Тест чата
        bot_response = f"Ваш запрос: '{user_text}' никуда не отправлен"
        bot_message = Vertical(
            Static(f"[dim][{time_str}][/dim] [bold]LLM:[/bold]"),
            Static(Markdown(bot_response)),
            classes = "chat-message bot-message"
        )
        chat_log.mount(bot_message)

        event.input.value = ""
        chat_log.scroll_end(animate=False)


if __name__ == "__main__":
    app = ExperementalTUI()
    app.run()