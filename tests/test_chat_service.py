import pytest

from gpt4free_tui_cli.application.chat_service import ChatService, SendMessage
from gpt4free_tui_cli.domain.events import Completed, Failed, TextDelta
from gpt4free_tui_cli.domain.models import Message
from gpt4free_tui_cli.testing.scripted_provider import ScriptedProvider


class FakeChats:
    def __init__(self) -> None:
        self.saved: list[tuple[int, str, str]] = []

    def get_context_messages(self, chat_id: int, limit: int) -> list[Message]:
        assert (chat_id, limit) == (7, 2)
        return [
            Message(role="user", content="старый вопрос"),
            Message(role="assistant", content="старый ответ"),
        ]

    def save_message(self, chat_id: int, role: str, content: str) -> None:
        self.saved.append((chat_id, role, content))


class FakeSettings:
    def __init__(self) -> None:
        self.saved: list[tuple[str, str | None]] = []

    def save_last_selection(self, *, model: str, provider: str | None) -> None:
        self.saved.append((model, provider))


@pytest.mark.asyncio
async def test_chat_service_uses_one_context_policy_and_persists_completed_turn() -> (
    None
):
    provider = ScriptedProvider((TextDelta("новый "), TextDelta("ответ"), Completed()))
    chats = FakeChats()
    settings = FakeSettings()
    service = ChatService(
        provider=provider, chats=chats, settings=settings, context_limit=2
    )

    events = [
        event
        async for event in service.send(
            SendMessage(7, "новый вопрос", "offline-model", "offline")
        )
    ]

    assert events == [TextDelta("новый "), TextDelta("ответ"), Completed()]
    assert provider.requests[0].messages == (
        Message(role="user", content="старый вопрос"),
        Message(role="assistant", content="старый ответ"),
        Message(role="user", content="новый вопрос"),
    )
    assert chats.saved == [
        (7, "user", "новый вопрос"),
        (7, "assistant", "новый ответ"),
    ]
    assert settings.saved == [("offline-model", "offline")]


@pytest.mark.asyncio
async def test_chat_service_does_not_persist_error_as_assistant_message() -> None:
    chats = FakeChats()
    settings = FakeSettings()
    service = ChatService(
        provider=ScriptedProvider((Failed("недоступен"),)),
        chats=chats,
        settings=settings,
        context_limit=2,
    )

    events = [
        event
        async for event in service.send(SendMessage(7, "новый вопрос", "offline-model"))
    ]

    assert events == [Failed("недоступен")]
    assert chats.saved == [(7, "user", "новый вопрос")]
    assert settings.saved == []
