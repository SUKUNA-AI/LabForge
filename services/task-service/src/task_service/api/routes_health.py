from fastapi import APIRouter, Response, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from task_service.infrastructure.db.session import get_async_engine
from task_service.schemas.responses import HealthLiveResponse, HealthReadyResponse

router = APIRouter(prefix="/api/v1", tags=["health"])
legacy_router = APIRouter(tags=["health"])


@router.get(
    "/health/live",
    response_model=HealthLiveResponse,
    status_code=status.HTTP_200_OK,
)
async def health_live() -> HealthLiveResponse:
    return HealthLiveResponse(status="ok")


@legacy_router.get(
    "/health",
    response_model=HealthLiveResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def legacy_health_check() -> HealthLiveResponse:
    return await health_live()


@router.get(
    "/health/ready",
    response_model=HealthReadyResponse,
    status_code=status.HTTP_200_OK,
)
async def health_ready(response: Response) -> HealthReadyResponse:
    try:
        async with get_async_engine().connect() as connection:
            await connection.execute(text("select 1"))
    except SQLAlchemyError:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthReadyResponse(status="error", database="unavailable")

    return HealthReadyResponse(status="ok", database="available")
