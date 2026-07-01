from textual.widgets import Static

class BotLoading(Static):
    """Кастомный индикатор загрузки"""
    
    def on_mount(self) -> None:
        self.frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.idx = 0
        self.set_interval(0.08, self.update_spinner)

    def update_spinner(self) -> None:
        self.update(f"[bold $accent]{self.frames[self.idx]}[/]")
        self.idx = (self.idx + 1) % len(self.frames)