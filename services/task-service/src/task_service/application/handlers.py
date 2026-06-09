from collections.abc import Sequence

from task_service.application.commands import (
    CreateTaskCommand,
    GetTaskCommand,
    ListTasksCommand,
    PutTaskCommand,
    UpdateTaskCommand,
)
from task_service.application.errors import TaskConflict, TaskNotFound
from task_service.application.results import PutTaskResult
from task_service.domain.task import Task
from task_service.infrastructure.db.unit_of_work import AbstractUnitOfWork


async def create_task(command: CreateTaskCommand, uow: AbstractUnitOfWork) -> Task:
    async with uow:
        task = Task(
            title=command.title,
            description=command.description,
            priority=command.priority,
            project_uid=command.project_uid,
            source_type=command.source_type,
            source_uid=command.source_uid,
        )

        await uow.tasks.add(task)
        await uow.commit()

        return task


async def put_task(command: PutTaskCommand, uow: AbstractUnitOfWork) -> PutTaskResult:
    async with uow:
        existing_task = await uow.tasks.get_by_uid(command.uid)

        if existing_task is None:
            task = Task(
                uid=command.uid,
                title=command.title,
                description=command.description,
                priority=command.priority,
                project_uid=command.project_uid,
                source_type=command.source_type,
                source_uid=command.source_uid,
            )
            await uow.tasks.add(task)
            await uow.commit()
            return PutTaskResult(task=task, created=True)

        if _task_matches_put_command(existing_task, command):
            return PutTaskResult(task=existing_task, created=False)

        raise TaskConflict(f"Task with uid {command.uid} already exists")


async def get_task(command: GetTaskCommand, uow: AbstractUnitOfWork) -> Task:
    async with uow:
        task = await uow.tasks.get_by_uid(command.uid)

        if task is None:
            raise TaskNotFound(f"Task with uid {command.uid} was not found")

        return task


async def list_tasks(
    command: ListTasksCommand,
    uow: AbstractUnitOfWork,
) -> Sequence[Task]:
    async with uow:
        return await uow.tasks.list(
            project_uid=command.project_uid,
            status=command.status,
            priority=command.priority,
            source_type=command.source_type,
            limit=command.limit,
            offset=command.offset,
        )


async def count_tasks(
    command: ListTasksCommand,
    uow: AbstractUnitOfWork,
) -> int:
    async with uow:
        return await uow.tasks.count(
            project_uid=command.project_uid,
            status=command.status,
            priority=command.priority,
            source_type=command.source_type,
        )


async def update_task(command: UpdateTaskCommand, uow: AbstractUnitOfWork) -> Task:
    async with uow:
        task = await uow.tasks.get_by_uid(command.uid)

        if task is None:
            raise TaskNotFound(f"Task with uid {command.uid} was not found")

        if _field_should_update(command, "title"):
            task.change_title(command.title)
        if _field_should_update(command, "description"):
            task.change_description(command.description)
        if _field_should_update(command, "status"):
            task.change_status(command.status)
        if _field_should_update(command, "priority"):
            task.change_priority(command.priority)
        if _field_should_update(command, "project_uid"):
            task.change_project_uid(command.project_uid)
        if _field_should_update(command, "source_type"):
            task.change_source_type(command.source_type)
        if _field_should_update(command, "source_uid"):
            task.change_source_uid(command.source_uid)

        updated_task = await uow.tasks.update(task)

        if updated_task is None:
            raise TaskNotFound(f"Task with uid {command.uid} was not found")

        await uow.commit()

        return updated_task


def _task_matches_put_command(task: Task, command: PutTaskCommand) -> bool:
    return (
        task.title == command.title
        and task.description == command.description
        and task.priority == command.priority
        and task.project_uid == command.project_uid
        and task.source_type == command.source_type
        and task.source_uid == command.source_uid
    )


def _field_should_update(command: UpdateTaskCommand, field_name: str) -> bool:
    if command.fields_set is not None:
        return field_name in command.fields_set

    return getattr(command, field_name) is not None
