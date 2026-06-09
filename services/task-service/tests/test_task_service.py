import os
import sys
import unittest
from collections.abc import Sequence
from pathlib import Path
from uuid import UUID

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:qwerty@localhost:5432/labforge_task_service",
)

TASK_SERVICE_SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(TASK_SERVICE_SRC))

from fastapi.testclient import TestClient

from task_service.application import handlers
from task_service.application.commands import (
    CreateTaskCommand,
    GetTaskCommand,
    ListTasksCommand,
    UpdateTaskCommand,
)
from task_service.application.errors import TaskNotFound
from task_service.domain.enums import TaskPriority, TaskSourceType, TaskStatus
from task_service.domain.task import Task
from task_service.main import app


class FakeTaskRepository:
    def __init__(self) -> None:
        self._tasks: dict[UUID, Task] = {}

    async def add(self, task: Task) -> None:
        self._tasks[task.uid] = task

    async def get_by_uid(self, uid: UUID) -> Task | None:
        return self._tasks.get(uid)

    async def list(
        self,
        project_uid: UUID | None = None,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        source_type: TaskSourceType | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[Task]:
        tasks = list(self._tasks.values())

        if project_uid is not None:
            tasks = [task for task in tasks if task.project_uid == project_uid]
        if status is not None:
            tasks = [task for task in tasks if task.status == status]
        if priority is not None:
            tasks = [task for task in tasks if task.priority == priority]
        if source_type is not None:
            tasks = [task for task in tasks if task.source_type == source_type]

        return tasks[offset : offset + limit]

    async def count(
        self,
        project_uid: UUID | None = None,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        source_type: TaskSourceType | None = None,
    ) -> int:
        return len(
            await self.list(
                project_uid=project_uid,
                status=status,
                priority=priority,
                source_type=source_type,
            )
        )

    async def update(self, task: Task) -> Task | None:
        if task.uid not in self._tasks:
            return None

        self._tasks[task.uid] = task
        return task

    async def delete(self, uid: UUID) -> bool:
        return self._tasks.pop(uid, None) is not None


class FakeUnitOfWork:
    def __init__(self, tasks: FakeTaskRepository | None = None) -> None:
        self.tasks = tasks or FakeTaskRepository()
        self.commits = 0
        self.rollbacks = 0

    async def __aenter__(self) -> "FakeUnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            await self.rollback()

    async def commit(self) -> None:
        self.commits += 1

    async def rollback(self) -> None:
        self.rollbacks += 1


class TaskApplicationTests(unittest.IsolatedAsyncioTestCase):
    async def test_create_get_list_and_count_task(self) -> None:
        uow = FakeUnitOfWork()

        created = await handlers.create_task(
            CreateTaskCommand(title="Write tests", priority=TaskPriority.HIGH),
            uow,
        )

        fetched = await handlers.get_task(GetTaskCommand(uid=created.uid), uow)
        listed = await handlers.list_tasks(
            ListTasksCommand(status=TaskStatus.TODO, priority=TaskPriority.HIGH),
            uow,
        )
        count = await handlers.count_tasks(
            ListTasksCommand(status=TaskStatus.TODO, priority=TaskPriority.HIGH),
            uow,
        )

        self.assertEqual(fetched.uid, created.uid)
        self.assertEqual([task.uid for task in listed], [created.uid])
        self.assertEqual(count, 1)
        self.assertEqual(uow.commits, 1)

    async def test_patch_can_clear_nullable_fields_and_change_status(self) -> None:
        task = Task(
            title="Clear description",
            description="temporary text",
            priority=TaskPriority.MEDIUM,
        )
        uow = FakeUnitOfWork()
        await uow.tasks.add(task)

        updated = await handlers.update_task(
            UpdateTaskCommand(
                uid=task.uid,
                description=None,
                status=TaskStatus.COMPLETED,
                fields_set=frozenset({"description", "status"}),
            ),
            uow,
        )

        self.assertIsNone(updated.description)
        self.assertEqual(updated.status, TaskStatus.COMPLETED)
        self.assertEqual(uow.commits, 1)

    async def test_get_missing_task_raises_not_found(self) -> None:
        missing_uid = Task(title="Existing task", priority=TaskPriority.LOW).uid

        with self.assertRaises(TaskNotFound):
            await handlers.get_task(GetTaskCommand(uid=missing_uid), FakeUnitOfWork())


class TaskApiContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_openapi_exposes_only_resource_oriented_task_paths(self) -> None:
        paths = set(app.openapi()["paths"])

        self.assertIn("/api/v1/tasks", paths)
        self.assertIn("/api/v1/tasks/{uid}", paths)
        self.assertIn("/api/v1/tasks/profile", paths)
        self.assertNotIn("/api/v1/tasks/{uid}/complete", paths)
        self.assertNotIn("/api/v1/tasks/{uid}/cancel", paths)
        self.assertNotIn("/api/v1/profiles/task", paths)

    def test_task_profile_documents_patch_status_updates(self) -> None:
        response = self.client.get("/api/v1/tasks/profile")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("completed", body["statuses"])
        self.assertIn("cancelled", body["statuses"])
        self.assertEqual(
            body["actions"]["update"],
            {"method": "PATCH", "href": "/api/v1/tasks/{uid}"},
        )
        self.assertNotIn("complete", body["actions"])
        self.assertNotIn("cancel", body["actions"])

    def test_health_live_and_legacy_health_are_available(self) -> None:
        self.assertEqual(self.client.get("/api/v1/health/live").json(), {"status": "ok"})
        self.assertEqual(self.client.get("/health").json(), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
