from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from task_service.infrastructure.db.models import Task
from task_service.schemas.task import TaskCreate, TaskRead, TaskUpdate
from task_service.infrastructure.db.session import get_db

router = APIRouter()

@router.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreate, db: AsyncSession = Depends(get_db)):
    db_task = Task(**task_data.model_dump())
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task
    

@router.get("/tasks", response_model=list[TaskRead])
async def get_all_tasks(db: AsyncSession = Depends(get_db)):
    query = select(Task)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/tasks/{task_id}", response_model=TaskRead)
async def get_task_by_id(task_id: int, db: AsyncSession = Depends(get_db)):
    db_task_by_id = await db.get(Task, task_id)

    if db_task_by_id is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return db_task_by_id


@router.patch("/tasks/{task_id}", response_model=TaskRead)
async def update_task_by_id(task_id: int, task_data: TaskUpdate, db: AsyncSession = Depends(get_db)):
    db_task_by_id = await db.get(Task, task_id)

    if db_task_by_id is None:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_data.model_dump(exclude_unset=True)

    for k, v in update_data.items():
        setattr(db_task_by_id, k, v)

    await db.commit()
    await db.refresh(db_task_by_id)

    return db_task_by_id
