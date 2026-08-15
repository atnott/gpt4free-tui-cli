"""Переходный adapter существующего SQLite manager к application port."""

from gpt4free_tui_cli.core.database import DatabaseManager
from gpt4free_tui_cli.domain.models import Message, MessageRole


class SQLiteChatRepository:
    def __init__(self, database: DatabaseManager) -> None:
        self._database = database

    def get_context_messages(self, chat_id: int, limit: int) -> list[Message]:
        rows = self._database.get_chat_history(chat_id, limit)
        return [
            Message(role=row["role"], content=row["content"])
            for row in rows
            if row["role"] in ("user", "assistant") and row["content"]
        ]

    def save_message(self, chat_id: int, role: MessageRole, content: str) -> None:
        self._database.save_message(chat_id, role, content)
