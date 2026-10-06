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
    # SQLite stores done as 0/1; the API should keep returning true/false
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
    }


def get_all_tasks():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM tasks").fetchall()
        return [row_to_task(row) for row in rows]
    finally:
        conn.close()


def get_task_by_id(task_id):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        return row_to_task(row) if row else None
    finally:
        conn.close()

def insert_task(title):
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (title, 0),
        )
        conn.commit()
        new_id = cursor.lastrowid
    finally:
        conn.close()
    return get_task_by_id(new_id)



def update_task_row(task_id, title, done):
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
            (title, 1 if done else 0, task_id),
        )
        conn.commit()
    finally:
        conn.close()
    return get_task_by_id(task_id)


def delete_task_row(task_id):
    conn = get_connection()
    try:
        cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()