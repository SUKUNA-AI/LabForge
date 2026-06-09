from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from task_service.application.errors import TaskConflict, TaskNotFound
from task_service.domain.errors import TaskDomainError
from task_service.schemas.responses import ApiErrorResponse


def _error_response(
    request: Request,
    *,
    status_code: int,
    title: str,
    detail: str,
    error_type: str,
) -> JSONResponse:
    body = ApiErrorResponse(
        type=error_type,
        title=title,
        status=status_code,
        detail=detail,
        instance=str(request.url.path),
    )
    return JSONResponse(status_code=status_code, content=jsonable_encoder(body))


async def task_not_found_handler(request: Request, exc: TaskNotFound) -> JSONResponse:
    return _error_response(
        request,
        status_code=status.HTTP_404_NOT_FOUND,
        title="Task not found",
        detail=str(exc),
        error_type="task_not_found",
    )


async def task_conflict_handler(request: Request, exc: TaskConflict) -> JSONResponse:
    return _error_response(
        request,
        status_code=status.HTTP_409_CONFLICT,
        title="Task conflict",
        detail=str(exc),
        error_type="task_conflict",
    )


async def task_domain_error_handler(request: Request, exc: TaskDomainError) -> JSONResponse:
    return _error_response(
        request,
        status_code=status.HTTP_400_BAD_REQUEST,
        title="Invalid task",
        detail=str(exc),
        error_type="invalid_task",
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(TaskNotFound, task_not_found_handler)
    app.add_exception_handler(TaskConflict, task_conflict_handler)
    app.add_exception_handler(TaskDomainError, task_domain_error_handler)
