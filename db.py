import sqlite3
from pathlib import Path

# tasks.db lives next to this file, no matter where you launch the server from
DB_FILE = Path(__file__).parent / "tasks.db"

SEED_TASKS = [
    ("Learn HTTP basics", 1),
    ("Build a CRUD API", 0),
    ("Publish to GitHub", 0),
]


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # lets us read columns by name
    return conn


def init_db():
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                SEED_TASKS,
            )

        conn.commit()
    finally:
        conn.close()