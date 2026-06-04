# LabForge

LabForge - учебно-практический backend/AI-проект для инженерной памяти: задачи, эксперименты, заметки, агентные сценарии и работа с LLM.

Сейчас реализован первый сервис: `task-service`.

## Что Уже Есть

- FastAPI `task-service`
- асинхронная работа с PostgreSQL через SQLAlchemy
- миграции Alembic в async-режиме
- Pydantic-схемы для задач
- endpoints для задач:
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
- `title`
- `description`
- `status`
- `priority`
- `created_at`
- `updated_at`

Текущие статусы:

- `To Do`
- `In Progress`
- `In Review`
- `Testing`
- `Completed`

## Что Дальше

Ближайшие следующие шаги:

- вынести бизнес-логику из роутеров в application/service слой
- добавить repository-слой
- добавить тесты для `task-service`
- добавить `experiment-service`
- позже подключить `agent-service`, `llm-service`, `gateway-service`, `note-service`
- отдельно добавить C++ `preprocessing-service`
