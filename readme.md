# Task API

A small to-do list API built with Python and FastAPI. It supports full CRUD (create, read, update, delete) on tasks stored in a PostgreSQL database that runs in Docker. The whole stack (API and database) starts with one command.

Built for the FlyRank Internship, Backend Track. Storage evolved in three steps without changing the endpoints: in-memory (A1), SQLite (A2), containerized Postgres (A3).

## Requirements

- Docker Desktop (or Docker Engine with the Compose plugin)

No Python or Postgres installation is needed to run it.

## Run everything with one command

```bash
git clone https://github.com/AbhinavBh18/task-api
cd task-api
cp .env.example .env
docker compose up
```

(On Windows PowerShell, use `copy .env.example .env` instead of `cp`.)

The API runs at `http://localhost:8000`. Swagger UI is at `http://localhost:8000/docs`.

On first run the app creates the `tasks` table and seeds three example tasks. The seed runs only when the table is empty, so restarting never duplicates them.

Stop with `Ctrl+C`, then `docker compose down`. Your data is kept in a Docker volume, so it is still there on the next `docker compose up`. To wipe it, run `docker compose down -v`.

## Configuration

Settings live in `.env` (git-ignored). `.env.example` lists every key:

| Variable | Purpose |
|----------|---------|
| `POSTGRES_USER` | Database user |
| `POSTGRES_PASSWORD` | Database password |
| `POSTGRES_DB` | Database name |
| `DATABASE_URL` | Connection string used when running the app outside Docker |

Inside Docker Compose, the API builds its own connection string from these values and reaches the database through the service name `db`. No credentials are hardcoded in the code or in `compose.yaml`.


## Authentication

The API uses **Supabase Auth** as its Identity Provider. Supabase stores the
accounts, hashes passwords and signs JSON Web Tokens (JWTs); this API never
stores a password. Protected routes verify the caller's token with Supabase
before running.

### Supabase setup

1. Create a free project at supabase.com.
2. Copy the **Project URL** and the **anon** key from Project Settings → API
   (never use the `service_role` key).
3. Turn **Confirm email** off under Authentication → Sign In / Providers → Email
   (practice project only).
4. Put both values in `.env` (see `.env.example`).

### Auth endpoints

| Method | Path | Description | Auth needed | Success | Errors |
|--------|------|-------------|-------------|---------|--------|
| POST | `/auth/signup` | Create an account | No | 201 | 400 |
| POST | `/auth/login` | Log in, returns access + refresh token | No | 200 | 400, 401 |
| POST | `/auth/logout` | End the session | Bearer token | 204 | 401 |
| GET | `/public/info` | Public message | No | 200 | |
| GET | `/protected/profile` | Current user's id, email, signup date | Bearer token | 200 | 401 |
| GET | `/protected/dashboard` | Second protected route (same guard) | Bearer token | 200 | 401 |

Send the token as `Authorization: Bearer <access_token>`.

### How it works

A single FastAPI dependency (`get_current_user` in `auth.py`) reads the bearer
token and asks Supabase to verify it. Any route that declares
`Depends(get_current_user)` is protected, with no auth code repeated. Missing,
malformed, expired or tampered tokens all return `401` with a JSON error.

### Swagger UI

Open `/docs`, log in via `POST /auth/login`, click **Authorize**, paste the
access token (without the word `Bearer`), then use **Try it out** on any
protected route.

![Swagger with bearer auth](docs/swagger-auth.png)

### Notes

- Logout calls Supabase's sign-out, but a JWT is stateless: an already-issued
  access token stays valid until it expires (about an hour). This is the
  tradeoff behind short-lived access tokens and refresh tokens.
- The `/tasks` routes from earlier assignments are not protected yet.




## Endpoints

| Method | Path | Description | Success | Errors |
|--------|------|-------------|---------|--------|
| GET | `/` | API info | 200 | |
| GET | `/health` | Health check | 200 | |
| GET | `/tasks` | List all tasks | 200 | |
| GET | `/tasks/{id}` | Get one task | 200 | 404 |
| POST | `/tasks` | Create a task (`{"title": "..."}`) | 201 | 400 |
| PUT | `/tasks/{id}` | Update title and/or done | 200 | 400, 404 |
| DELETE | `/tasks/{id}` | Delete a task | 204 | 404 |

Errors return JSON like `{"error": "Task not found"}`. All SQL uses parameterized queries (`%s` placeholders), so user input is never glued into SQL strings.

## Example request

HTTP/1.1 200 OK
date: Tue, 06 Oct 2026 18:28:15 GMT
server: uvicorn
content-length: 198
content-type: application/json

## Swagger UI

![Swagger UI](docs/swagger.png)

## The data in Postgres

![tasks table in Postgres via psql](docs/postgres-psql.png)

## Persistence

Postgres stores its files in the named volume `taskdata`, which lives outside the container. `docker compose down` removes the containers but keeps the volume, so tasks survive a full restart.

## Running without Docker (optional)

Start a Postgres database, set `DATABASE_URL` in `.env` to point at it (host `localhost`), then:

```bash
python -m venv venv
venv\Scripts\activate        # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
fastapi dev main.py
```

## Project structure

- `main.py`: FastAPI routes and request validation
- `db.py`: all database code (connection, table creation, seeding, queries)
- `Dockerfile`: builds the API image
- `compose.yaml`: runs the API and Postgres together
- `.env.example`: template for the settings file
- `requirements.txt`: dependencies