import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

# read DATABASE_URL from the .env file next to this file
load_dotenv(Path(__file__).parent / ".env")
DATABASE_URL = os.environ["DATABASE_URL"]

SEED_TASKS = [
    ("Learn HTTP basics", True),
    ("Build a CRUD API", False),
    ("Publish to GitHub", False),
]


def get_connection():
    # dict_row lets us read columns by name, like sqlite3.Row did
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def init_db():
    # "with" commits on success and closes the connection at the end
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT FALSE
            )
            """
        )

        count = conn.execute("SELECT COUNT(*) AS n FROM tasks").fetchone()["n"]
        if count == 0:
            with conn.cursor() as cur:
                cur.executemany(
                    "INSERT INTO tasks (title, done) VALUES (%s, %s)",
                    SEED_TASKS,
                )

def row_to_task(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "done": row["done"],
    }

def get_all_tasks():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM tasks ORDER BY id").fetchall()
        return [row_to_task(row) for row in rows]

def get_task_by_id(task_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM tasks WHERE id = %s", (task_id,)
        ).fetchone()
        return row_to_task(row) if row else None


def insert_task(title):
    with get_connection() as conn:
        row = conn.execute(
            "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING *",
            (title, False),
        ).fetchone()
        return row_to_task(row)



def update_task_row(task_id, title, done):
    with get_connection() as conn:
        row = conn.execute(
            "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING *",
            (title, done, task_id),
        ).fetchone()
        return row_to_task(row) if row else None


def delete_task_row(task_id):
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        return cursor.rowcount > 0

    