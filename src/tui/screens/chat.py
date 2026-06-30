from textual.screen import Screen
from textual.containers import Horizontal, Vertical
from textual.widgets import Placeholder
from tui.widgets.chat_log import ChatLog
from tui.widgets.chat_input import ChatInput

class ChatScreen(Screen):
    def compose(self):
        """Экран чата сайдбар с настройками и чат с логом"""
        with Horizontal():
            yield Vertical(
                Placeholder(),
                id="sidebar_panel") 
            
            with Vertical(id="chat_panel"):
                yield ChatLog(id="chat_log")
                yield ChatInput(id="chat_input")

            yield Vertical(
                Placeholder(),
                id = "info_panel"
            )