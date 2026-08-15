"""Неизменяемые значения, передаваемые между application и provider port."""

from dataclasses import dataclass
from typing import Literal


MessageRole = Literal["user", "assistant"]


@dataclass(frozen=True, slots=True)
class Message:
    """Обычное текстовое сообщение диалога."""

    role: MessageRole
    content: str

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise ValueError("Содержимое сообщения не может быть пустым.")


@dataclass(frozen=True, slots=True)
class ModelRequest:
    """Один запрос к модели с уже сформированным контекстом."""

    model: str
    messages: tuple[Message, ...]
    provider: str | None = None
    web_search: bool = False

    def __post_init__(self) -> None:
        if not self.model.strip():
            raise ValueError("Имя модели не может быть пустым.")
        if not self.messages:
            raise ValueError("Запрос к модели должен содержать хотя бы одно сообщение.")
