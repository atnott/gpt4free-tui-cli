"""Детерминированная замена g4f stream для offline-тестов."""

from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ScriptedProvider:
    """Возвращает заданные chunks и сохраняет каждый запрос для проверки."""

    chunks: Sequence[str]
    requests: list[dict[str, Any]] = field(default_factory=list)

    async def get_chat_stream(
        self,
        *,
        model: str,
        message: str | None = None,
        messages: list[dict[str, Any]] | None = None,
        provider: str | None = None,
        web_search: bool = False,
    ) -> AsyncIterator[str]:
        self.requests.append(
            {
                "model": model,
                "message": message,
                "messages": messages,
                "provider": provider,
                "web_search": web_search,
            }
        )
        for chunk in self.chunks:
            yield chunk
