from textual.widgets import Static
from textual.containers import Vertical
from rich.markdown import Markdown as RichMarkdown
from tui.widgets.bot_loading import BotLoading

class BotMessage(Vertical):
    """Контейнер для ответа нейросети"""
    def __init__(self, text: str = "", id = None):
        super().__init__(id = id)
        self.raw_text = text
        self.bubble = Static(classes = "bubble")
        self.spinner = BotLoading()

    def compose(self):
        yield self.spinner
        yield self.bubble

    def on_mount(self) -> None:
        if self.raw_text:
            self.spinner.display = False
            self.update_content(self.raw_text)
        else:
            self.bubble.display = False

    def update_content(self, new_text: str) -> None:
        """Метод для динамического обновления текста модели"""
        if self.spinner.display:
            self.spinner.display = False
            self.bubble.display = True

        self.raw_text = new_text
        self.bubble.update(RichMarkdown(self.raw_text, code_theme="monokai"))