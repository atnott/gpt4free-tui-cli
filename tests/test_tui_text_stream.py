from types import SimpleNamespace

from core.engine import G4FEngine
from tui.tui_core.chat_processor import process_chat_stream


class FakeDatabase:
    def __init__(self) -> None:
        self.saved_messages: list[tuple[int, str, str | None]] = []

    def get_all_chat_messages(self, chat_id: int):
        return [
            {"role": "user", "content": "старый вопрос"},
            {"role": "tool_call", "content": None},
            {"role": "assistant", "content": "старый ответ"},
        ]

    def save_message(self, chat_id: int, role: str, content: str | None = None) -> None:
        self.saved_messages.append((chat_id, role, content))


class FakeEngine:
    def __init__(self) -> None:
        self.request: dict | None = None

    async def get_chat_stream(self, **kwargs):
        self.request = kwargs
        yield "<tool_call>"
        yield '{"name":"python_execute"}'
        yield "</tool_call>"


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


async def test_tui_forwards_tool_markup_as_plain_text_without_executing_it() -> None:
    database = FakeDatabase()
    engine = FakeEngine()
    app = SimpleNamespace(
        current_chat_id=7,
        MAX_CONTEXT=20,
        model="test-model",
        provider="test-provider",
        db=database,
        engine=engine,
    )
    chat_log = FakeChatLog()

    await process_chat_stream(app, chat_log, "новый вопрос")

    assert engine.request == {
        "model": "test-model",
        "messages": [
            {"role": "user", "content": "старый вопрос"},
            {"role": "assistant", "content": "старый ответ"},
            {"role": "user", "content": "новый вопрос"},
        ],
        "provider": "test-provider",
    }
    assert (
        chat_log.bot_message.content
        == '<tool_call>{"name":"python_execute"}</tool_call>'
    )
    assert database.saved_messages == [
        (7, "user", "новый вопрос"),
        (7, "assistant", '<tool_call>{"name":"python_execute"}</tool_call>'),
    ]


def test_engine_has_no_tool_stream_api() -> None:
    assert not hasattr(G4FEngine, "get_chat_stream_with_tools")
