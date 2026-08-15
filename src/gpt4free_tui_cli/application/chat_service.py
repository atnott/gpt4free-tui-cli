"""Один provider-neutral use case отправки сообщения."""

import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass

from gpt4free_tui_cli.application.context_builder import build_context
from gpt4free_tui_cli.domain.events import (
    Cancelled,
    Completed,
    Failed,
    ProviderEvent,
    TextDelta,
)
from gpt4free_tui_cli.domain.models import ModelRequest
from gpt4free_tui_cli.ports.model_provider import ModelProvider
from gpt4free_tui_cli.ports.repositories import ChatRepository
from gpt4free_tui_cli.ports.settings import Settings


@dataclass(frozen=True, slots=True)
class SendMessage:
    chat_id: int
    prompt: str
    model: str
    provider: str | None = None
    web_search: bool = False


class ChatService:
    """Собирает контекст, сохраняет историю и нормализует ошибки провайдера."""

    def __init__(
        self,
        *,
        provider: ModelProvider,
        chats: ChatRepository,
        settings: Settings,
        context_limit: int = 20,
    ) -> None:
        self._provider = provider
        self._chats = chats
        self._settings = settings
        self._context_limit = context_limit

    async def send(self, command: SendMessage) -> AsyncIterator[ProviderEvent]:
        history = self._chats.get_context_messages(command.chat_id, self._context_limit)
        request = ModelRequest(
            model=command.model,
            messages=build_context(
                history, command.prompt, max_messages=self._context_limit
            ),
            provider=command.provider,
            web_search=command.web_search,
        )
        self._chats.save_message(command.chat_id, "user", command.prompt)

        response_parts: list[str] = []
        try:
            async for event in self._provider.stream(request):
                if isinstance(event, TextDelta):
                    response_parts.append(event.text)
                    yield event
                    continue
                if isinstance(event, Failed | Cancelled):
                    yield event
                    return
                if isinstance(event, Completed):
                    self._complete(command, "".join(response_parts))
                    yield event
                    return
        except asyncio.CancelledError:
            yield Cancelled()
        except Exception:
            yield Failed("Провайдер не смог завершить запрос.")
        else:
            self._complete(command, "".join(response_parts))
            yield Completed()

    def _complete(self, command: SendMessage, response: str) -> None:
        if response.strip():
            self._chats.save_message(command.chat_id, "assistant", response)
        self._settings.save_last_selection(
            model=command.model, provider=command.provider
        )
