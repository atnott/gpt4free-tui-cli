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

    def get_chat_history(self, chat_id: int) -> list[sqlite3.Row]:
        '''Возвращает последние десять сообщений диалога'''
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT role, content FROM messages 
            WHERE chat_id = ?
            ORDER BY created_at
            ASC
            ''', (chat_id,))
            rows = cursor.fetchall()
            return rows[-10:]