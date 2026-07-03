from textual.containers import Vertical
from textual.widgets import Static

class UserMessage(Vertical):
    """Контейнер для сообщения пользователя"""
    def __init__(self, text: str, id = None):
        super().__init__(id = id)
        self.text = text

    def compose(self):
        # Область с текстом.
        yield Static(self.text, classes="bubble")