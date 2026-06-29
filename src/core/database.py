import sqlite3
from pathlib import Path

class DatabaseManager:
    def __init__(self) -> None:
        self.path_dir = Path(__file__).resolve().parent.parent.parent
        self.db_path = self.path_dir / 'storage.db'

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn


