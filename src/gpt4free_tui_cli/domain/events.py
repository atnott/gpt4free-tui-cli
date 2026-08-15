"""Типизированные результаты одного streaming turn."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TextDelta:
    text: str

    def __post_init__(self) -> None:
        if not self.text:
            raise ValueError("TextDelta не может быть пустым.")


@dataclass(frozen=True, slots=True)
class Completed:
    """Провайдер успешно завершил ответ."""


@dataclass(frozen=True, slots=True)
class Failed:
    """Ошибка, нормализованная на границе application service."""

    message: str


@dataclass(frozen=True, slots=True)
class Cancelled:
    """Отмена запроса вызывающим кодом."""


ProviderEvent = TextDelta | Completed | Failed | Cancelled
