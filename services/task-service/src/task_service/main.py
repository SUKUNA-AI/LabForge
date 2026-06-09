from fastapi import FastAPI

from task_service.api.routes_health import legacy_router as legacy_health_router
from task_service.api.routes_health import router as health_router
from task_service.api.routes_tasks import router as tasks_router
from task_service.api.errors import register_error_handlers

app = FastAPI(title="LabForge Task Service")
register_error_handlers(app)

app.include_router(legacy_health_router)
app.include_router(health_router)
app.include_router(tasks_router)
