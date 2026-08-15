import importlib.util
from types import SimpleNamespace

import pytest

from gpt4free_tui_cli.domain.events import Completed, TextDelta
from gpt4free_tui_cli.tui.tui_core.chat_processor import process_chat_stream


class FakeChatService:
    def __init__(self) -> None:
        self.command = None

    async def send(self, command):
        self.command = command
        yield TextDelta('<tool_call>{"name":"python_execute"}</tool_call>')
        yield Completed()


class FakeBotMessage:
    def __init__(self) -> None:
        self.content = ""

    def stop_loading(self) -> None:
        pass

    def update_content(self, content: str) -> None:
        self.content = content


class FakeChatLog:
    def __init__(self) -> None:
        self.bot_message = FakeBotMessage()

    def append_message(self, text: str, is_user: bool):
        return self.bot_message

    def scroll_end(self, animate: bool) -> None:
        pass


@pytest.mark.asyncio
async def test_tui_forwards_tool_markup_as_plain_text_without_executing_it() -> None:
    service = FakeChatService()
    app = SimpleNamespace(
        current_chat_id=7,
        model="test-model",
        provider="test-provider",
        chat_service=service,
    )
    chat_log = FakeChatLog()

    await process_chat_stream(app, chat_log, "новый вопрос")

    assert service.command is not None
    assert service.command.chat_id == 7
    assert service.command.prompt == "новый вопрос"
    assert (
        chat_log.bot_message.content
        == '<tool_call>{"name":"python_execute"}</tool_call>'
    )


def test_removed_tool_package_is_not_importable() -> None:
    assert importlib.util.find_spec("gpt4free_tui_cli.core.tools") is None
