# LabForge

LabForge - учебно-практический backend/AI-проект для инженерной памяти: задачи, эксперименты, заметки, агентные сценарии и работа с LLM.

Сейчас реализован первый сервис: `task-service`.

## Что Уже Есть

- FastAPI `task-service`
- асинхронная работа с PostgreSQL через SQLAlchemy
- миграции Alembic в async-режиме
- domain model для задач: `Task`, статусы, приоритеты, source types и доменные ошибки
- repository-слой: `AbstractTaskRepository`, `SqlAlchemyTaskRepository`, mapper `TaskModel <-> Task`
- Unit of Work для управления `AsyncSession`, `commit` и `rollback`
- application layer: commands, handlers и application errors
- подготовка REST API-контракта: request/response schemas, public `uid`, list metadata и standard error schema
- текущие legacy endpoints для задач:
  - `POST /tasks`
  - `GET /tasks`
  - `GET /tasks/{task_id}`
  - `PATCH /tasks/{task_id}`
  - `GET /health`

## Структура

```text
services/
  task-service/
    src/
      task_service/
        api/
          routes_health.py
          routes_tasks.py
        application/
          commands.py
          errors.py
          handlers.py
          results.py
        adapters/
          repositories/
            task_mapper.py
            task_repository.py
            sqlalchemy_task_repository.py
        domain/
          enums.py
          errors.py
          task.py
        infrastructure/
          db/
            base.py
            models.py
            session.py
            unit_of_work.py
        schemas/
          requests.py
          responses.py
          task.py
        main.py

migrations/
  task_service/
    env.py
    versions/

main.py
alembic.ini
```

Корневой `main.py` нужен для удобного локального запуска из корня проекта.

## Переменные Окружения

Создай локальный `.env` в корне проекта. Этот файл не коммитится.

Минимально нужно:

```env
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/labforge_task_service
```

Пример с локальным PostgreSQL:

```env
DATABASE_URL=postgresql+asyncpg://postgres:qwerty@localhost:5432/labforge_task_service
```

## Установка Зависимостей

```powershell
pip install fastapi uvicorn sqlalchemy alembic asyncpg python-dotenv pydantic
```

## Миграции

Применить миграции:

```powershell
alembic upgrade head
```

Проверить текущую миграцию:

```powershell
alembic current
```

Проверить, что модели и миграции синхронизированы:

```powershell
alembic check
```

## Запуск

Из корня проекта:

```powershell
uvicorn main:app --reload
```

После запуска Swagger будет доступен здесь:

```text
http://127.0.0.1:8000/docs
```

А health-check здесь:

```text
http://127.0.0.1:8000/health
```

## Модель Задачи

Задача сейчас хранит:

- `id`
- `uid`
- `project_uid`
- `title`
- `description`
- `status`
- `priority`
- `source_type`
- `source_uid`
- `created_at`
- `updated_at`

Текущие статусы:

- `todo`
- `in_progress`
- `in_review`
- `testing`
- `completed`
- `cancelled`

Текущие приоритеты:

- `low`
- `medium`
- `high`
- `critical`

Текущие source types:

- `manual`
- `agent_run`
- `experiment`
- `note`
- `research`
- `weekly_review`
- `architecture_review`

## Архитектурный Поток

Внутренний поток для use-case слоя:

```text
application handler
  -> UnitOfWork
     -> TaskRepository
        -> task_mapper
           -> TaskModel / PostgreSQL
```

Цель этого разделения: роуты должны принимать HTTP, собирать command, вызывать handler и отдавать response. SQLAlchemy, `commit`, `select` и `TaskModel` не должны жить в API routes после следующего этапа рефакторинга.

## Что Дальше

Ближайшие следующие шаги:

- завершить REST API слой под `/api/v1`
- добавить presenters: `Task -> TaskResponse`, list response с `items/meta/links`
- добавить standard error builders в Problem Details style
- добавить pagination helpers: default `limit=50`, max `limit=100`, `offset>=0`
- переписать `routes_tasks.py`, чтобы он шёл через `request -> command -> handler -> presenter`
- добавить `health/live`, `health/ready` и `profiles/task`
- добавить unit/integration/API tests для `task-service`
- добавить `experiment-service`
- позже подключить `agent-service`, `llm-service`, `gateway-service`, `note-service`
- отдельно добавить C++ `preprocessing-service`
