"""Детерминированный provider port для offline contract-тестов."""

from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass, field

from gpt4free_tui_cli.domain.events import ProviderEvent
from gpt4free_tui_cli.domain.models import ModelRequest


@dataclass
class ScriptedProvider:
    """Возвращает заданные события и сохраняет каждый подготовленный запрос."""

    events: Sequence[ProviderEvent]
    requests: list[ModelRequest] = field(default_factory=list)

    async def stream(self, request: ModelRequest) -> AsyncIterator[ProviderEvent]:
        self.requests.append(request)
        for event in self.events:
            yield event
