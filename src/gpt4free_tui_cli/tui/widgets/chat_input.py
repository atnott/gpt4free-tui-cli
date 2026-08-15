from textual.widgets import Input
from gpt4free_tui_cli.tui.tui_core.chat_processor import process_chat_stream


class ChatInput(Input):
    def __init__(self, id=None):
        super().__init__(placeholder="[Space] Input your request...", id=id)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        prompt = event.value.strip()
        if not prompt:
            return

        self.value = ""

        chat_log = self.screen.query_one("#chat_log")

        await process_chat_stream(app=self.app, chat_log=chat_log, prompt=prompt)
