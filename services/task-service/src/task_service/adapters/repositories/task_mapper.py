from task_service.domain.enums import TaskPriority, TaskSourceType, TaskStatus
from task_service.infrastructure.db.models import TaskModel
from task_service.domain.task import Task

def to_domain(model: TaskModel) -> Task:
    return Task(
  id=model.id,
  uid=model.uid,
  project_uid=model.project_uid,
  title=model.title,
  description=model.description,
  status=TaskStatus(model.status),
  priority=TaskPriority(model.priority),
  source_type=TaskSourceType(model.source_type),
  source_uid=model.source_uid,
  created_at=model.created_at,
  updated_at=model.updated_at,
)


def to_model(task: Task) -> TaskModel:
    return TaskModel(
  uid=task.uid,
  project_uid=task.project_uid,
  title=task.title,
  description=task.description,
  status=task.status.value,
  priority=task.priority.value,
  source_type=task.source_type.value,
  source_uid=task.source_uid,
  created_at=task.created_at,
  updated_at=task.updated_at,
)


def update_model_from_entity(model: TaskModel, task: Task) -> TaskModel:
    model.project_uid = task.project_uid
    model.title = task.title
    model.description = task.description
    model.status = task.status.value
    model.priority = task.priority.value
    model.source_type = task.source_type.value
    model.source_uid = task.source_uid
    model.updated_at = task.updated_at

    return model