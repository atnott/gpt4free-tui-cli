"""Интерфейс стримингового провайдера модели."""

from collections.abc import AsyncIterator
from typing import Protocol

from gpt4free_tui_cli.domain.events import ProviderEvent
from gpt4free_tui_cli.domain.models import ModelRequest


class ModelProvider(Protocol):
    """Выполняет ровно один подготовленный model turn."""

    def stream(self, request: ModelRequest) -> AsyncIterator[ProviderEvent]: ...
