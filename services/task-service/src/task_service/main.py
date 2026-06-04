from fastapi import FastAPI

from task_service.api.routes_health import router as health_router
from task_service.api.routes_tasks import router as tasks_router

app = FastAPI(title="LabForge Task Service")

app.include_router(health_router)
app.include_router(tasks_router)
