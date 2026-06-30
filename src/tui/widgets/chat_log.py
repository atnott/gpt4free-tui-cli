from textual.containers import VerticalScroll
from tui.widgets.bot_message import BotMessage
from tui.widgets.user_message import UserMessage

class ChatLog(VerticalScroll):
    def __init__(self, id = None):
        super().__init__(id = id)

    def append_message(self, text: str, is_user: bool):

        if is_user:
            msg_widget = UserMessage(text)
        else:
            msg_widget = BotMessage(text)
            
        self.mount(msg_widget)
        self.scroll_end(animate=False)
        return msg_widget