import sqlite3
from pathlib import Path

class DatabaseManager:
    def __init__(self) -> None:
        self.path_dir = Path(__file__).resolve().parent.parent.parent
        self.db_path = self.path_dir / 'storage.db'
        self._init_db()

    def _get_connection(self):
        '''Возвращает соединение с базой данных'''
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        '''Создает таблицы в базе данных и инициализирует дефолтный чат'''
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );''')
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES chats (id) ON DELETE CASCADE
            );''')
            cursor.execute('''
            INSERT OR IGNORE INTO chats (id, title)
            VALUES (1, 'Основной диалог')
            ''')

    def save_message(self, chat_id: int, role: str, content: str) -> None:
        '''Сохраняет сообщение в базу данных'''
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT OR IGNORE INTO messages (chat_id, role, content)
            VALUES (?, ?, ?)''', (chat_id, role, content))

    def get_chat_history(self, chat_id: int, limit: int = 10) -> list[sqlite3.Row]:
        '''Возвращает последние N сообщений для контекста'''
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT role, content FROM (
                SELECT id, role, content FROM messages 
                WHERE chat_id = ?
                ORDER BY id DESC
                LIMIT ?
            ) ORDER BY id ASC
            ''', (chat_id, limit))
            return cursor.fetchall()

    def get_all_chat_messages(self, chat_id: int) -> list[sqlite3.Row]:
        '''Возвращает все сообщения диалога для отрисовки на экране'''
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT role, content FROM messages 
            WHERE chat_id = ?
            ORDER BY id ASC
            ''', (chat_id,))
            return cursor.fetchall()

    def create_chat(self, title: str) -> int:
        '''Создает новую сессию чата и возвращает ее id'''
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO chats (title) VALUES (?)
            ''', (title,))
            return cursor.lastrowid

    def get_all_chats(self) -> list[sqlite3.Row]:
        '''Возвращает список всех чатов'''
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT id, title, created_at FROM chats
            ORDER BY id
            DESC
            ''')
            return cursor.fetchall()

    def delete_chat(self, chat_id: int) -> None:
        '''Удаляет сессию чата'''
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            DELETE FROM chats WHERE id = ?
            ''', (chat_id,))