from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll, Vertical
from textual.widgets import Placeholder, Input, Header, Footer, Static
from datetime import datetime
from rich.markdown import Markdown

from ....core.engine import G4FEngine

class ExperementalTUI(App):
    CSS_PATH = "styles/tui_styles.tcss"
    DEFAULT_MODEL = "gpt-4o"

    def compose(self) -> ComposeResult:
        """ Разметка интерфейса Textual

        Returns:
            ComposeResult: Интерфейс TUI

        Yields:
            Iterator[ComposeResult]: Итерируется header, основной контейнер Horizontal и footer интерфейса
        """
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
        
        self.engine = G4FEngine()
        self.current_model = self.DEFAULT_MODEL


    #Ввод пользователя
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """При вводе пользователя отправляет текст выбранной модели, в лог чата,
        очищает область ввода и делает потоковый вывод модели в Markdown

        Args:
            event (Input.Submitted): Текст отправляется в лог и к модели
        """

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
        # Очистка окна ввода
        event.input.value = ""
        chat_log.scroll_end(animate=False)

        bot_content_widget = Static("")
        bot_message = Vertical(
            Static(f"[dim][{time_str}][/dim] [bold green]LLM {self.current_model}:[/bold green]"),
            bot_content_widget,
            classes="chat-message bot-message"
        )

        chat_log.mount(bot_message)
        chat_log.scroll_end(animate=False)

        bot_content_widget.loading = True
        full_response = ""

        try:
            async_stream = self.engine.get_chat_stream(
                model=self.current_model,
                message=user_text
            )

            async for chunk in async_stream:
                if bot_content_widget.loading:
                    bot_content_widget.loading = False

                full_response += chunk
                bot_content_widget.update(Markdown(full_response))
                chat_log.scroll_end(animate=False)

        except Exception as e:
            bot_content_widget.loading = False
            bot_content_widget.update(f"[bold red]Ошибка API:[/bold red] {e}")
            chat_log.scroll_end(animate=False)


if __name__ == "__main__":
    app = ExperementalTUI()
    app.run()