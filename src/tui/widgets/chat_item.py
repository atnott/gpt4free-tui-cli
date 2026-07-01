from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Button

class ChatItem(Widget):
    """Компонент одной строки чата в списке"""
    
    def __init__(self, chat_id: int, title: str, is_active: bool = False) -> None:
        super().__init__(id=f"chat_item_{chat_id}")
        self.chat_id = chat_id
        self.chat_title = title
        self.is_active = is_active

    def compose(self) -> ComposeResult:
        with Horizontal(classes="chat-item-row"):
            yield Button(
                self.chat_title, 
                id="btn_select", 
                classes="active-chat" if self.is_active else ""
            )
            yield Button("R", id="btn_rename", classes="btn-action")
            yield Button("D", id="btn_delete", classes="btn-action variant-error")