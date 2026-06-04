# LabForge

LabForge is a backend/AI engineering-memory project built as a FastAPI microservice system. The first working milestone is `task-service`: a small async FastAPI service that stores tasks in PostgreSQL through SQLAlchemy and Alembic migrations.

## Current Status

Implemented:

- Async FastAPI `task-service`
- PostgreSQL persistence for tasks
- SQLAlchemy async sessions
- Alembic migrations in async mode
- Task endpoints:
  - `POST /tasks`
  - `GET /tasks`
  - `GET /tasks/{task_id}`
  - `PATCH /tasks/{task_id}`
  - `GET /health`

Planned next services:

- `experiment-service`
- `llm-service`
- `agent-service`
- `gateway-service`
- `note-service`
- C++ `preprocessing-service`

## Project Layout

```text
services/
  task-service/
    src/
      task_service/
        api/
          routes_health.py
          routes_tasks.py
        infrastructure/
          db/
            base.py
            models.py
            session.py
        schemas/
          task.py
        main.py

migrations/
  task_service/
    env.py
    versions/

alembic.ini
```

## Configuration

Create a local `.env` file in the repository root. Do not commit it.

Required variable:

```env
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/labforge_task_service
```

The project uses the async PostgreSQL driver `asyncpg`.

## Database

Run migrations from the repository root:

```bash
alembic upgrade head
```

Check migration state:

```bash
alembic current
```

Check whether SQLAlchemy models and migrations are in sync:

```bash
alembic check
```

## Running Task Service

Install the needed Python packages in your environment:

```bash
pip install fastapi uvicorn sqlalchemy alembic asyncpg python-dotenv pydantic
```

Start the service from the repository root:

```bash
set PYTHONPATH=services/task-service/src
uvicorn task_service.main:app --reload
```

On PowerShell:

```powershell
$env:PYTHONPATH="services/task-service/src"
uvicorn task_service.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

## Task Model

Current task fields:

- `id`
- `title`
- `description`
- `status`
- `priority`
- `created_at`
- `updated_at`

Current statuses:

- `To Do`
- `In Progress`
- `In Review`
- `Testing`
- `Completed`

## Git Hygiene

Ignored by default:

- `.env` and local secrets
- Python caches and virtual environments
- build outputs
- PostgreSQL dumps and local data
- C++/CMake generated artifacts
- all Markdown drafts except `README.md`

Tracked:

- source code
- Alembic migration files
- service structure
- root `README.md`
