from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Response, status

from task_service.api.pagination import pagination_params
from task_service.api.presenters import task_to_response, tasks_to_list_response
from task_service.application import handlers
from task_service.application.commands import (
    CreateTaskCommand,
    GetTaskCommand,
    ListTasksCommand,
    PutTaskCommand,
    UpdateTaskCommand,
)
from task_service.domain.enums import TaskPriority, TaskSourceType, TaskStatus
from task_service.infrastructure.db.unit_of_work import AbstractUnitOfWork, SqlAlchemyUnitOfWork
from task_service.schemas.requests import TaskCreateRequest, TaskPutRequest, TaskUpdateRequest
from task_service.schemas.responses import TaskListResponse, TaskProfileResponse, TaskResponse


router = APIRouter(prefix="/api/v1", tags=["tasks"])


def get_uow() -> AbstractUnitOfWork:
    return SqlAlchemyUnitOfWork()


@router.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    request: TaskCreateRequest,
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> TaskResponse:
    task = await handlers.create_task(
        CreateTaskCommand(
            title=request.title,
            description=request.description,
            priority=request.priority,
            project_uid=request.project_uid,
            source_type=request.source_type,
            source_uid=request.source_uid,
        ),
        uow,
    )

    return task_to_response(task)


@router.get("/tasks", response_model=TaskListResponse)
async def list_tasks(
    request: Request,
    pagination: tuple[int, int] = Depends(pagination_params),
    project_uid: UUID | None = None,
    status_filter: TaskStatus | None = Query(default=None, alias="status"),
    priority: TaskPriority | None = None,
    source_type: TaskSourceType | None = None,
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> TaskListResponse:
    limit, offset = pagination

    command = ListTasksCommand(
        project_uid=project_uid,
        status=status_filter,
        priority=priority,
        source_type=source_type,
        limit=limit,
        offset=offset,
    )
    filters = {
        "project_uid": project_uid,
        "status": status_filter,
        "priority": priority,
        "source_type": source_type,
    }

    tasks = await handlers.list_tasks(command, uow)
    count = await handlers.count_tasks(command, get_uow())

    return tasks_to_list_response(
        tasks=tasks,
        limit=limit,
        offset=offset,
        count=count,
        base_url=str(request.url.path),
        filters=filters,
    )


@router.get("/tasks/profile", response_model=TaskProfileResponse)
async def get_tasks_profile(request: Request) -> TaskProfileResponse:
    return TaskProfileResponse(
        fields={
            "uid": {"type": "uuid", "read_only": True},
            "title": {
                "type": "string",
                "required": True,
                "min_length": 3,
                "max_length": 255,
            },
            "description": {"type": "string", "required": False},
            "status": {"type": "enum", "required": False},
            "priority": {"type": "enum", "required": False},
            "project_uid": {"type": "uuid", "required": False},
            "source_type": {"type": "enum", "required": False},
            "source_uid": {"type": "uuid", "required": False},
            "created_at": {"type": "datetime", "read_only": True},
            "updated_at": {"type": "datetime", "read_only": True},
        },
        statuses=[item.value for item in TaskStatus],
        priorities=[item.value for item in TaskPriority],
        source_types=[item.value for item in TaskSourceType],
        actions={
            "create": {"method": "POST", "href": "/api/v1/tasks"},
            "list": {"method": "GET", "href": "/api/v1/tasks"},
            "get": {"method": "GET", "href": "/api/v1/tasks/{uid}"},
            "put": {"method": "PUT", "href": "/api/v1/tasks/{uid}"},
            "update": {"method": "PATCH", "href": "/api/v1/tasks/{uid}"},
            "profile": {"method": "GET", "href": "/api/v1/tasks/profile"},
        },
        links={
            "self": str(request.url.path),
            "tasks": "/api/v1/tasks",
            "health": "/api/v1/health/ready",
        },
    )


@router.get("/tasks/{uid}", response_model=TaskResponse)
async def get_task(
    uid: UUID,
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> TaskResponse:
    task = await handlers.get_task(GetTaskCommand(uid=uid), uow)
    return task_to_response(task)


@router.put("/tasks/{uid}", response_model=TaskResponse)
async def put_task(
    uid: UUID,
    request: TaskPutRequest,
    response: Response,
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> TaskResponse:
    result = await handlers.put_task(
        PutTaskCommand(
            uid=uid,
            title=request.title,
            description=request.description,
            priority=request.priority,
            project_uid=request.project_uid,
            source_type=request.source_type,
            source_uid=request.source_uid,
        ),
        uow,
    )

    if result.created:
        response.status_code = status.HTTP_201_CREATED

    return task_to_response(result.task)


@router.patch("/tasks/{uid}", response_model=TaskResponse)
async def update_task(
    uid: UUID,
    request: TaskUpdateRequest,
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> TaskResponse:
    task = await handlers.update_task(
        UpdateTaskCommand(
            uid=uid,
            title=request.title,
            description=request.description,
            status=request.status,
            priority=request.priority,
            project_uid=request.project_uid,
            source_type=request.source_type,
            source_uid=request.source_uid,
            fields_set=frozenset(request.model_fields_set),
        ),
        uow,
    )

    return task_to_response(task)
