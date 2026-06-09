from collections.abc import Sequence

from task_service.api.pagination import pagination_href
from task_service.domain.task import Task
from task_service.schemas.responses import (
    ActionResponse,
    PaginationLinksResponse,
    TaskListMetaResponse,
    TaskListResponse,
    TaskResponse,
)


def build_task_links(task: Task) -> dict[str, str]:
    return {
        "self": f"/api/v1/tasks/{task.uid}",
        "list": "/api/v1/tasks",
    }


def task_to_response(task: Task) -> TaskResponse:
    return TaskResponse(
        uid=task.uid,
        project_uid=task.project_uid,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        source_type=task.source_type,
        source_uid=task.source_uid,
        created_at=task.created_at,
        updated_at=task.updated_at,
        links=build_task_links(task),
        actions=build_task_actions(task),
    )


def build_task_actions(task: Task) -> dict[str, ActionResponse]:
    return {
        "update": ActionResponse(
            method="PATCH",
            href=f"/api/v1/tasks/{task.uid}",
        ),
    }


def tasks_to_list_response(
    tasks: Sequence[Task],
    limit: int,
    offset: int,
    count: int,
    base_url: str,
    filters: dict[str, object | None] | None = None,
) -> TaskListResponse:
    next_offset = offset + limit
    prev_offset = max(offset - limit, 0)

    next_link = None
    if next_offset < count:
        next_link = pagination_href(
            base_url,
            limit=limit,
            offset=next_offset,
            filters=filters,
        )

    prev_link = None
    if offset > 0:
        prev_link = pagination_href(
            base_url,
            limit=limit,
            offset=prev_offset,
            filters=filters,
        )

    return TaskListResponse(
        items=[task_to_response(task) for task in tasks],
        meta=TaskListMetaResponse(
            limit=limit,
            offset=offset,
            count=count,
        ),
        links=PaginationLinksResponse(
            self=pagination_href(
                base_url,
                limit=limit,
                offset=offset,
                filters=filters,
            ),
            next=next_link,
            prev=prev_link,
        ),
    )
