from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(
    title="Task API",
    description="A small to-do list API with full CRUD, stored in memory.",
    version="1.0",
)

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


@app.get("/", summary="API info", description="Describes this API and lists its main endpoints.")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"],
    }


@app.get("/health", summary="Health check", description="Returns ok if the server is alive.")
def health_check():
    return {"status": "ok"}


@app.get("/tasks", summary="List all tasks", description="Returns every task in the in-memory list.")
def list_tasks():
    return tasks


@app.get(
    "/tasks/{task_id}",
    summary="Get one task",
    description="Returns the task with the given id.",
    responses={404: {"description": "Task not found"}},
)
def get_task(task_id: int):
    task = find_task(task_id)
    if task is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} not found"},
        )
    return task


@app.post(
    "/tasks",
    status_code=201,
    summary="Create a task",
    description="Creates a task from a title. The server assigns the id and sets done to false.",
    responses={400: {"description": "Title missing or empty"}},
)
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


@app.put(
    "/tasks/{task_id}",
    summary="Update a task",
    description="Changes a task's title and/or done status. Send at least one of them.",
    responses={
        400: {"description": "Empty body or empty title"},
        404: {"description": "Task not found"},
    },
)
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


@app.delete(
    "/tasks/{task_id}",
    status_code=204,
    summary="Delete a task",
    description="Removes the task with the given id. Returns no content on success.",
    responses={404: {"description": "Task not found"}},
)
def delete_task(task_id: int):
    task = find_task(task_id)
    if task is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} not found"},
        )
    tasks.remove(task)
    return Response(status_code=204)