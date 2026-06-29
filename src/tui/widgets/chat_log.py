from textual.containers import VerticalScroll

class ChatLog(VerticalScroll):
    def __init__(self, id = None):
        super().__init__(id = id)