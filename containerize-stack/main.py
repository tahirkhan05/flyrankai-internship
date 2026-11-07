import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import psycopg
from psycopg.rows import dict_row

# Load environment secrets from .env
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:dev@localhost:5432/tasks")

app = FastAPI()

def get_db():
    """Connect to PostgreSQL using DATABASE_URL from environment."""
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)

def init_db():
    """Create tasks table if missing and seed starter tasks on empty count."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    done BOOLEAN NOT NULL DEFAULT FALSE
                )
            """)
            cursor.execute("SELECT COUNT(*) FROM tasks")
            count = cursor.fetchone()["count"]

            if count == 0:
                seed_tasks = [
                    ("Set up project", True),
                    ("Build Stage 2 endpoints", False),
                    ("Write documentation", False),
                ]
                cursor.executemany(
                    "INSERT INTO tasks (title, done) VALUES (%s, %s)",
                    seed_tasks,
                )
        conn.commit()

# Run database setup on startup
init_db()

class TaskCreate(BaseModel):
    title: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


@app.get("/")
def root():
    """Return API metadata and endpoints."""
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
def health():
    """Health check endpoint to verify server status."""
    return {"status": "ok"}


@app.get("/tasks")
def get_tasks():
    """List all tasks from PostgreSQL."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, title, done FROM tasks")
            rows = cursor.fetchall()
            return [
                {"id": row["id"], "title": row["title"], "done": row["done"]}
                for row in rows
            ]


@app.get("/tasks/{id}")
def get_task(id: int):
    """Retrieve a single task by ID from PostgreSQL using a parameterized query."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, title, done FROM tasks WHERE id = %s", (id,))
            row = cursor.fetchone()
            if row is None:
                return JSONResponse(status_code=404, content={"error": "Task not found"})
            return {"id": row["id"], "title": row["title"], "done": row["done"]}


@app.post("/tasks", status_code=201)
def create_task(task_input: TaskCreate):
    """Create a new task in the SQLite database."""
    if not task_input.title or not task_input.title.strip():
        return JSONResponse(status_code=400, content={"error": "Title is required and cannot be empty"})

    title = task_input.title.strip()

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (title, 0))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return {
        "id": new_id,
        "title": title,
        "done": False,
    }


@app.put("/tasks/{id}")
def update_task(id: int, task_input: TaskUpdate):
    """Update an existing task's title or status using parameterized SQL."""
    if task_input.title is None and task_input.done is None:
        return JSONResponse(status_code=400, content={"error": "Body cannot be empty; provide title and/or done"})
    if task_input.title is not None and not task_input.title.strip():
        return JSONResponse(status_code=400, content={"error": "Title cannot be empty"})

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (id,))
    existing = cursor.fetchone()
    if existing is None:
        conn.close()
        return JSONResponse(status_code=404, content={"error": "Task not found"})

    new_title = task_input.title.strip() if task_input.title is not None else existing["title"]
    new_done = int(task_input.done) if task_input.done is not None else existing["done"]

    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (new_title, new_done, id)
    )
    conn.commit()
    conn.close()

    return {
        "id": id,
        "title": new_title,
        "done": bool(new_done)
    }


@app.delete("/tasks/{id}")
def delete_task(id: int):
    """Delete a task by ID using parameterized SQL."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (id,))
    conn.commit()
    deleted_rows = cursor.rowcount
    conn.close()

    if deleted_rows == 0:
        return JSONResponse(status_code=404, content={"error": "Task not found"})

    return Response(status_code=204)