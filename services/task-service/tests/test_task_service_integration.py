import os
import sys
import unittest
from pathlib import Path
from uuid import UUID

TASK_SERVICE_SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(TASK_SERVICE_SRC))


@unittest.skipUnless(
    os.getenv("RUN_TASK_SERVICE_INTEGRATION_TESTS") == "1",
    "set RUN_TASK_SERVICE_INTEGRATION_TESTS=1 to run PostgreSQL integration tests",
)
class TaskServiceIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        import httpx

        from task_service.main import app

        self.httpx = httpx
        self.transport = httpx.ASGITransport(app=app)
        self.client = httpx.AsyncClient(
            transport=self.transport,
            base_url="http://testserver",
        )
        self.created_uids: list[str] = []

    async def asyncTearDown(self) -> None:
        from sqlalchemy import delete

        from task_service.infrastructure.db.models import TaskModel
        from task_service.infrastructure.db.session import (
            dispose_async_engine,
            get_async_session_maker,
        )

        await self.client.aclose()

        if self.created_uids:
            async with get_async_session_maker()() as session:
                await session.execute(
                    delete(TaskModel).where(
                        TaskModel.uid.in_([UUID(uid) for uid in self.created_uids])
                    )
                )
                await session.commit()

        await dispose_async_engine()

    async def test_task_crud_smoke_with_postgresql(self) -> None:
        create_response = await self.client.post(
            "/api/v1/tasks",
            json={
                "title": "Integration smoke task",
                "description": "temporary integration record",
                "priority": "high",
                "source_type": "manual",
            },
        )
        self.assertEqual(create_response.status_code, 201, create_response.text)
        created = create_response.json()
        self.created_uids.append(created["uid"])

        get_response = await self.client.get(f"/api/v1/tasks/{created['uid']}")
        self.assertEqual(get_response.status_code, 200, get_response.text)
        self.assertEqual(get_response.json()["uid"], created["uid"])

        patch_response = await self.client.patch(
            f"/api/v1/tasks/{created['uid']}",
            json={"description": None, "status": "completed"},
        )
        self.assertEqual(patch_response.status_code, 200, patch_response.text)
        patched = patch_response.json()
        self.assertIsNone(patched["description"])
        self.assertEqual(patched["status"], "completed")

        list_response = await self.client.get(
            "/api/v1/tasks",
            params={"status": "completed", "priority": "high", "limit": 10},
        )
        self.assertEqual(list_response.status_code, 200, list_response.text)
        listed = list_response.json()
        self.assertGreaterEqual(listed["meta"]["count"], 1)
        self.assertTrue(
            any(item["uid"] == created["uid"] for item in listed["items"]),
            listed,
        )
