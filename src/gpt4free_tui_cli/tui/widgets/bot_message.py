from textual.widgets import Static
from textual.containers import Vertical
from rich.markdown import Markdown as RichMarkdown
from gpt4free_tui_cli.tui.widgets.bot_loading import BotLoading

class BotMessage(Vertical):
    """Контейнер для ответа нейросети"""
    def __init__(self, text: str | None = "", id = None):
        super().__init__(id = id)
        self.raw_text = text if text is not None else ""
        self.bubble = Static(classes="bubble")
        self.spinner = BotLoading()
        self.loading_active = text is not None

    def compose(self):
        yield self.spinner
        yield self.bubble

    def on_mount(self) -> None:
        if not self.loading_active or self.raw_text:
            self.disable_spinner()
            self.update_content(self.raw_text)
        else:
            self.bubble.display = False

    def stop_loading(self) -> None:
        """Публичный метод для явного отключения индикатора загрузки процессором"""
        self.loading_active = False
        self.disable_spinner()

    def disable_spinner(self) -> None:
        self.spinner.display = False
        self.bubble.display = True
        try:
            self.spinner.remove() 
        except Exception:
            pass
        self.refresh(layout=True)

    def update_content(self, new_text: str) -> None:
        """Метод для динамического обновления текста модели"""
        if self.loading_active:
            self.stop_loading()

        self.raw_text = new_text
        self.bubble.update(RichMarkdown(self.raw_text, code_theme="monokai"))
