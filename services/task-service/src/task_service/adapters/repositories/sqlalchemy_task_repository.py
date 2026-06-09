import uuid
from typing import Sequence
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from task_service.domain.enums import TaskPriority, TaskSourceType, TaskStatus
from task_service.infrastructure.db.models import TaskModel
from task_service.domain.task import Task
from task_service.adapters.repositories.task_repository import AbstractTaskRepository
from task_service.adapters.repositories.task_mapper import to_domain, to_model, update_model_from_entity


class SqlAlchemyTaskRepository(AbstractTaskRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _get_model_by_uid(self, uid: uuid.UUID) -> TaskModel | None:
        query = select(TaskModel).where(TaskModel.uid == uid)
        result = await self.session.execute(query)

        return result.scalar_one_or_none()
    
    async def add(self, task: Task) -> None:
        model = to_model(task)
        self.session.add(model)

    async def get_by_uid(self, uid:uuid.UUID) -> Task | None:
        model = await self._get_model_by_uid(uid)
        if model is None:
            return None
        
        return to_domain(model)
    
    async def list(
        self,
        project_uid: uuid.UUID | None = None,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        source_type: TaskSourceType | None = None,
        limit: int = 50,
        offset: int = 0
    ) -> Sequence[Task]:
        query = select(TaskModel)

        if project_uid is not None:
            query = query.where(TaskModel.project_uid == project_uid)

        if status is not None:
            query = query.where(TaskModel.status == status.value)

        if priority is not None:
            query = query.where(TaskModel.priority == priority.value)

        if source_type is not None:
            query = query.where(TaskModel.source_type == source_type.value)

        query = query.order_by(TaskModel.created_at.desc()).limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        models = result.scalars().all()
        
        return [to_domain(model) for model in models]

    async def count(
        self,
        project_uid: uuid.UUID | None = None,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        source_type: TaskSourceType | None = None,
    ) -> int:
        query = select(func.count()).select_from(TaskModel)

        if project_uid is not None:
            query = query.where(TaskModel.project_uid == project_uid)

        if status is not None:
            query = query.where(TaskModel.status == status.value)

        if priority is not None:
            query = query.where(TaskModel.priority == priority.value)

        if source_type is not None:
            query = query.where(TaskModel.source_type == source_type.value)

        result = await self.session.execute(query)
        return result.scalar_one()

    async def update(self, task: Task) -> Task | None:
        model = await self._get_model_by_uid(task.uid)

        if model is None:
            return None

        update_model_from_entity(model, task)

        return to_domain(model)

    async def delete(self, uid: uuid.UUID) -> bool:
        model = await self._get_model_by_uid(uid)

        if model is None:
            return False

        await self.session.delete(model)
        return True
