import pytest

from gpt4free_tui_cli.domain.events import Completed, TextDelta
from gpt4free_tui_cli.domain.models import Message, ModelRequest
from gpt4free_tui_cli.testing.scripted_provider import ScriptedProvider


@pytest.mark.asyncio
async def test_scripted_provider_is_deterministic_and_records_model_request() -> None:
    provider = ScriptedProvider((TextDelta("Привет"), TextDelta(" мир"), Completed()))
    request = ModelRequest(
        model="offline-model",
        messages=(Message(role="user", content="Тест"),),
        provider="offline",
    )

    events = [event async for event in provider.stream(request)]

    assert events == [TextDelta("Привет"), TextDelta(" мир"), Completed()]
    assert provider.requests == [request]
