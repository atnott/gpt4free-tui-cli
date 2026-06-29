from textual.widgets import Header

class AppHeader(Header):

    def __init__(self, show_clock = True, id = None):
        super().__init__(show_clock=show_clock, id=id)