from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from db import init_db, get_all_tasks, get_task_by_id, insert_task, update_task_row, delete_task_row
import supabase_client
from starlette.exceptions import HTTPException as StarletteHTTPException
from auth_routes import router as auth_router
from fastapi import FastAPI, Response, Header, HTTPException
from supabase import AuthApiError
from supabase_client import supabase
from fastapi import FastAPI, Response, Depends
from auth import get_current_user

init_db()
app = FastAPI(
    title="Task API",
    description="A small to-do list API with full CRUD, stored in a SQLite database.",
    version="1.0",
)
app.include_router(auth_router)


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
        headers=exc.headers,
    )
class TaskCreate(BaseModel):
    title: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


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


@app.get(
    "/public/info",
    tags=["public"],
    summary="Public info",
    description="Open to everyone. No token needed.",
)
def public_info():
    return {"message": "Welcome stranger! This info is public."}


@app.get(
    "/protected/profile",
    tags=["protected"],
    summary="Your profile (token required)",
    description="Requires an Authorization: Bearer <token> header.",
    responses={401: {"description": "Access token missing, invalid or expired"}},
)



@app.get(
    "/protected/profile",
    tags=["protected"],
    summary="Your profile (token required)",
    description="Returns the logged-in user's id, email and signup date.",
    responses={401: {"description": "Access token missing, invalid or expired"}},
)
def profile(user=Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at,
    }


@app.get(
    "/protected/dashboard",
    tags=["protected"],
    summary="Dashboard (token required)",
    description="A second protected route, guarded by the same dependency.",
    responses={401: {"description": "Access token missing, invalid or expired"}},
)
def dashboard(user=Depends(get_current_user)):
    return {"message": f"Welcome back, {user.email}"}




@app.get("/tasks", summary="List all tasks", description="Returns every task in the database.")
def list_tasks():
    return get_all_tasks()


@app.get(
    "/tasks/{task_id}",
    summary="Get one task",
    description="Returns the task with the given id.",
    responses={404: {"description": "Task not found"}},
)
def get_task(task_id: int):
    task = get_task_by_id(task_id)
    if task is None:
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"},
        )
    return task


@app.post(
    "/tasks",
    status_code=201,
    summary="Create a task",
    description="Creates a task from a title. The database assigns the id and done starts as false.",
    responses={400: {"description": "Title missing or empty"}},
)
def create_task(body: TaskCreate):
    if body.title is None or body.title.strip() == "":
        return JSONResponse(
            status_code=400,
            content={"error": "title is required and cannot be empty"},
        )

    return insert_task(body.title.strip())


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
    task = get_task_by_id(task_id)
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

    if body.title is not None and body.title.strip() == "":
        return JSONResponse(
            status_code=400,
            content={"error": "title cannot be empty"},
        )

    new_title = body.title.strip() if body.title is not None else task["title"]
    new_done = body.done if body.done is not None else task["done"]

    return update_task_row(task_id, new_title, new_done)


@app.delete(
    "/tasks/{task_id}",
    status_code=204,
    summary="Delete a task",
    description="Removes the task with the given id. Returns no content on success.",
    responses={404: {"description": "Task not found"}},
)
def delete_task(task_id: int):
    if not delete_task_row(task_id):
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"},
        )
    return Response(status_code=204)


