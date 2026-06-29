from textual.screen import Screen
from textual.containers import Horizontal, Vertical
from textual.widgets import Placeholder
from widgets.chat_log import ChatLog
from widgets.chat_input import ChatInput

class ChatScreen(Screen):
    """Экран чата сайдбар с настройками и чат с логом"""

    def compose(self):
        with Horizontal():
            yield Vertical(
                Placeholder(),
                id="sidebar_panel") 
            
            with Vertical(id="chat_panel"):
                yield ChatLog(id="chat_log")
                yield ChatInput(id="chat_input")