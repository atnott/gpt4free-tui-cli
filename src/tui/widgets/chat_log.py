from textual.containers import VerticalScroll
from textual.widgets import Static

class ChatLog(VerticalScroll):
    def __init__(self, id = None):
        super().__init__(id = id)

    def append_message(self, sender: str, text: str, color: str = "white") -> Static:
        msg_widget = Static(f"[bold {color}]{sender}:[/bold {color}]\n{text}\n")
        self.mount(msg_widget)
        self.scroll_end(animate=False)
        return msg_widget