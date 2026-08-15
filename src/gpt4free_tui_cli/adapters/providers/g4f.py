"""Адаптер g4f за provider-neutral port."""

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any

from g4f.Provider import __providers__
from g4f.client import AsyncClient

from gpt4free_tui_cli.domain.events import Completed, ProviderEvent, TextDelta
from gpt4free_tui_cli.domain.models import ModelRequest


class G4FModelProvider:
    """Преобразует g4f chunks в события единого provider port."""

    def __init__(self, client: AsyncClient | None = None) -> None:
        self._client = client or AsyncClient()

    async def stream(self, request: ModelRequest) -> AsyncIterator[ProviderEvent]:
        response = self._client.chat.completions.create(
            model=request.model,
            messages=[
                {"role": message.role, "content": message.content}
                for message in request.messages
            ],
            provider=request.provider,
            stream=True,
            web_search=request.web_search,
        )
        async for chunk in response:
            content = _extract_content(chunk)
            if content:
                yield TextDelta(content)
        yield Completed()


def _extract_content(chunk: Any) -> str:
    try:
        return str(chunk.choices[0].delta.content or "")
    except AttributeError:
        return str(chunk)


@dataclass(frozen=True, slots=True)
class ProviderStatus:
    name: str
    is_working: bool
    supported_models: tuple[str, ...]


class G4FCatalog:
    """Каталог g4f, отделённый от выполнения одного model turn."""

    def get_available_providers(self) -> list[ProviderStatus]:
        active: list[ProviderStatus] = []
        for provider in __providers__:
            is_working = bool(getattr(provider, "working", False))
            models = tuple(str(model) for model in getattr(provider, "models", []))
            if is_working and models:
                active.append(
                    ProviderStatus(
                        name=provider.__name__,
                        is_working=is_working,
                        supported_models=models,
                    )
                )
        return active

    def get_all_models(self) -> list[str]:
        return sorted(
            {
                model
                for provider in self.get_available_providers()
                for model in provider.supported_models
            }
        )
