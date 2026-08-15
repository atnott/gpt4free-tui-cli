from types import SimpleNamespace

import pytest

from gpt4free_tui_cli.adapters.providers.g4f import G4FModelProvider
from gpt4free_tui_cli.domain.events import Completed, TextDelta
from gpt4free_tui_cli.domain.models import Message, ModelRequest


class FakeCompletions:
    def __init__(self) -> None:
        self.kwargs = None

    def create(self, **kwargs):
        self.kwargs = kwargs

        async def response():
            yield SimpleNamespace(
                choices=[SimpleNamespace(delta=SimpleNamespace(content="первый "))]
            )
            yield SimpleNamespace(
                choices=[SimpleNamespace(delta=SimpleNamespace(content="второй"))]
            )

        return response()


@pytest.mark.asyncio
async def test_g4f_adapter_conforms_to_provider_event_contract_offline() -> None:
    completions = FakeCompletions()
    client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    provider = G4FModelProvider(client=client)
    request = ModelRequest(
        model="offline-model",
        messages=(Message(role="user", content="Тест"),),
        provider="offline",
    )

    events = [event async for event in provider.stream(request)]

    assert events == [TextDelta("первый "), TextDelta("второй"), Completed()]
    assert completions.kwargs == {
        "model": "offline-model",
        "messages": [{"role": "user", "content": "Тест"}],
        "provider": "offline",
        "stream": True,
        "web_search": False,
    }
