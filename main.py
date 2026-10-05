from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

tasks = [
    {"id": 1, "title": "Learn HTTP basics", "done": True},
    {"id": 2, "title": "Build a CRUD API", "done": False},
    {"id": 3, "title": "Publish to GitHub", "done": False},
]


class TaskCreate(BaseModel):
    title: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


def find_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


@app.get("/")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"],
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/tasks")
def list_tasks():
    return tasks


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = find_task(task_id)
    if task is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} not found"},
        )
    return task


@app.post("/tasks", status_code=201)
def create_task(body: TaskCreate):
    if body.title is None or body.title.strip() == "":
        return JSONResponse(
            status_code=400,
            content={"error": "title is required and cannot be empty"},
        )

    next_id = max((t["id"] for t in tasks), default=0) + 1
    new_task = {"id": next_id, "title": body.title.strip(), "done": False}
    tasks.append(new_task)
    return new_task


@app.put("/tasks/{task_id}")
def update_task(task_id: int, body: TaskUpdate):
    task = find_task(task_id)
    if task is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} not found"},
        )

    if body.title is None and body.done is None:
        return JSONResponse(
            status_code=400,
            content={"error": "provide title and/or done"},
        )

    if body.title is not None:
        if body.title.strip() == "":
            return JSONResponse(
                status_code=400,
                content={"error": "title cannot be empty"},
            )
        task["title"] = body.title.strip()

    if body.done is not None:
        task["done"] = body.done

    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    task = find_task(task_id)
    if task is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} not found"},
        )
    tasks.remove(task)
    return Response(status_code=204)