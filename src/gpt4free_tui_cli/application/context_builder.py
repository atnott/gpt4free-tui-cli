"""Единая политика короткого окна истории для всех presentation layers."""

from collections.abc import Sequence

from gpt4free_tui_cli.domain.models import Message


def build_context(
    history: Sequence[Message], prompt: str, *, max_messages: int
) -> tuple[Message, ...]:
    """Вернуть последние сообщения истории и новый prompt пользователя."""
    if max_messages < 1:
        raise ValueError("Размер окна контекста должен быть положительным.")

    current_message = Message(role="user", content=prompt)
    return (*history[-max_messages:], current_message)
