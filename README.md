# LabForge

LabForge - учебно-практический backend/AI-проект для инженерной памяти: задачи, эксперименты, заметки, агентные сценарии и работа с LLM.

Сейчас завершен первый сервис: `task-service`.

## Что Уже Готово

- FastAPI `task-service`
- асинхронная работа с PostgreSQL через SQLAlchemy
- миграции Alembic в async-режиме
- domain model для задач: `Task`, статусы, приоритеты, source types и доменные ошибки
- repository-слой: `AbstractTaskRepository`, `SqlAlchemyTaskRepository`, mapper `TaskModel <-> Task`
- Unit of Work для управления `AsyncSession`, `commit` и `rollback`
- application layer: commands, handlers, results и application errors
- REST API v1 через поток `request -> command -> handler -> presenter -> response`
- public `uid` для внешнего API
- list response с `items`, `meta`, `links`
- pagination helpers: `limit`, `offset`, `self`, `next`, `prev`
- presenters: `Task -> TaskResponse`
- standard error responses в стиле Problem Details
- health endpoints: live/ready
- profile endpoint для описания task-контракта
- unit/API contract tests на `unittest`

## API

Основной API живет под `/api/v1`.

### Tasks

```text
POST   /api/v1/tasks
GET    /api/v1/tasks
GET    /api/v1/tasks/profile
GET    /api/v1/tasks/{uid}
PUT    /api/v1/tasks/{uid}
PATCH  /api/v1/tasks/{uid}
```

`POST /api/v1/tasks` создает задачу.

`GET /api/v1/tasks` возвращает список задач с пагинацией и фильтрами:

- `limit`
- `offset`
- `status`
- `priority`
- `project_uid`
- `source_type`

`GET /api/v1/tasks/profile` возвращает описание доступных полей, статусов, приоритетов, source types, actions и links.

`GET /api/v1/tasks/{uid}` возвращает одну задачу по публичному `uid`.

`PUT /api/v1/tasks/{uid}` создает задачу с указанным `uid`, если ее еще нет. Если задача уже есть и данные совпадают, возвращает существующую. Если задача уже есть, но данные отличаются, возвращает конфликт.

`PATCH /api/v1/tasks/{uid}` частично обновляет задачу.

Завершение и отмена задачи тоже идут через `PATCH`:

```json
{
  "status": "completed"
}
```

```json
{
  "status": "cancelled"
}
```

Отдельных command endpoints вроде `/complete` и `/cancel` сейчас нет: для текущей модели это обычное изменение статуса.

### Health

```text
GET /api/v1/health/live
GET /api/v1/health/ready
GET /health
```

`/api/v1/health/live` проверяет, что приложение отвечает.

`/api/v1/health/ready` проверяет готовность приложения и доступность базы данных.

`/health` оставлен как legacy alias для простого локального health-check.

## Структура

```text
services/
  task-service/
    src/
      task_service/
        api/
          errors.py
          pagination.py
          presenters.py
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
    tests/
      test_task_service.py

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

Swagger:

```text
http://127.0.0.1:8000/docs
```

Health-check:

```text
http://127.0.0.1:8000/api/v1/health/live
```

## Тесты

Тесты написаны на стандартном `unittest`, поэтому отдельный `pytest` сейчас не нужен.

Запуск:

```powershell
python -m unittest discover -s services/task-service/tests -v
```

Дополнительная проверка синтаксиса:

```powershell
python -m compileall services/task-service/src/task_service services/task-service/tests
```

## Модель Задачи

Задача хранит:

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
HTTP request
  -> request schema
     -> command
        -> application handler
           -> UnitOfWork
              -> TaskRepository
                 -> task_mapper
                    -> TaskModel / PostgreSQL
           -> presenter
              -> response schema
```

Цель этого разделения: HTTP-слой принимает запрос, собирает command, вызывает application handler и отдает response. SQLAlchemy, `commit`, `select` и `TaskModel` не живут в API routes.

## Что Дальше

Ближайшие следующие шаги:

- добавить правила переходов статусов, если появится реальная workflow-логика
- добавить integration tests с реальной тестовой PostgreSQL
- добавить `experiment-service`
- позже подключить `agent-service`, `llm-service`, `gateway-service`, `note-service`
- отдельно добавить C++ `preprocessing-service`
