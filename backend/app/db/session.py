import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


def _db_path() -> str:
    return os.getenv("DB_PATH", "data/aulabot.db")


def _ensure_parent_exists(path: str) -> None:
    if path == ":memory:":
        return
    parent = Path(path).parent
    parent.mkdir(parents=True, exist_ok=True)


def init_db() -> None:
    path = _db_path()
    _ensure_parent_exists(path)
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_token TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                tool TEXT NOT NULL,
                input_chars INTEGER NOT NULL,
                output_chars INTEGER NOT NULL,
                prompt_tokens INTEGER NOT NULL,
                completion_tokens INTEGER NOT NULL,
                total_tokens INTEGER NOT NULL,
                estimated_cost REAL NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                embedding_json TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS monthly_aggregates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                year_month TEXT NOT NULL,
                total_tokens INTEGER NOT NULL,
                total_cost REAL NOT NULL,
                interaction_count INTEGER NOT NULL,
                UNIQUE(user_id, year_month),
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
            """
        )
        conn.commit()


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    path = _db_path()
    _ensure_parent_exists(path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

