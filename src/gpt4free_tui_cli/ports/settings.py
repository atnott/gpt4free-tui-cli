"""Небольшое сохраняемое состояние последнего успешного запроса."""

from typing import Protocol


class Settings(Protocol):
    def save_last_selection(self, *, model: str, provider: str | None) -> None: ...
