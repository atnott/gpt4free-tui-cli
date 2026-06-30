from textual.widgets import Static
from textual.containers import Vertical
from rich.markdown import Markdown as RichMarkdown

class BotMessage(Vertical):
    """Контейнер для ответа нейросети"""
    def __init__(self, text: str = "", id = None):
        super().__init__(id = id)
        self.raw_text = text
        # Создаем текстовый виджет заранее, чтобы обновлять его при стриминге
        self.bubble = Static(classes = "bubble")

    def compose(self):
        yield self.bubble

    def on_mount(self) -> None:
        self.update_content(self.raw_text)

    def update_content(self, new_text: str) -> None:
        """Метод для динамического обновления текста модели"""
        self.raw_text = new_text
        self.bubble.update(RichMarkdown(self.raw_text, code_theme="monokai"))