"""Хранилище истории, нужное единому use case отправки сообщения."""

from collections.abc import Sequence
from typing import Protocol

from gpt4free_tui_cli.domain.models import Message, MessageRole


class ChatRepository(Protocol):
    def get_context_messages(self, chat_id: int, limit: int) -> Sequence[Message]: ...

    def save_message(self, chat_id: int, role: MessageRole, content: str) -> None: ...
