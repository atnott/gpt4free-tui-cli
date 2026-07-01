from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from tui.widgets.chat_input import ChatInput
from tui.widgets.chat_log import ChatLog
from tui.widgets.choose_panel import ChoosePanel

class ChatScreen(Screen):

    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(id="sidebar_panel"):
                yield Vertical()
            
            with Vertical(id="chat_panel"):
                yield ChatLog(id="chat_log")
                yield ChatInput(id="chat_input")

            yield ChoosePanel(id="info_panel")