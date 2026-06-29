from textual.widgets import Input

class ChatInput(Input):
    def __init__(self, id = None):
        super().__init__(placeholder="Input your request...", id = id)