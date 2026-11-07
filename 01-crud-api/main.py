from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

tasks = [
    {"id": 1, "title": "Set up project", "done": True},
    {"id": 2, "title": "Build Stage 2 endpoints", "done": False},
    {"id": 3, "title": "Write documentation", "done": False},
]

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
    """List all tasks."""
    return tasks


@app.get("/tasks/{id}")
def get_task(id: int):
    """Get a single task by ID."""
    for task in tasks:
        if task["id"] == id:
            return task
    return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})


@app.post("/tasks", status_code=201)
def create_task(task_input: TaskCreate):
    """Create a new task."""
    if not task_input.title or not task_input.title.strip():
        return JSONResponse(status_code=400, content={"error": "Title is required and cannot be empty"})

    new_id = max([t["id"] for t in tasks], default=0) + 1
    new_task = {
        "id": new_id,
        "title": task_input.title.strip(),
        "done": False,
    }
    tasks.append(new_task)
    return new_task


@app.put("/tasks/{id}")
def update_task(id: int, task_input: TaskUpdate):
    """Update an existing task's title or status."""
    for task in tasks:
        if task["id"] == id:
            if task_input.title is None and task_input.done is None:
                return JSONResponse(status_code=400, content={"error": "Body cannot be empty; provide title and/or done"})
            if task_input.title is not None and not task_input.title.strip():
                return JSONResponse(status_code=400, content={"error": "Title cannot be empty"})

            if task_input.title is not None:
                task["title"] = task_input.title.strip()
            if task_input.done is not None:
                task["done"] = task_input.done
            return task

    return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})


@app.delete("/tasks/{id}")
def delete_task(id: int):
    """Delete a task by ID."""
    for i, task in enumerate(tasks):
        if task["id"] == id:
            tasks.pop(i)
            return Response(status_code=204)

    return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})