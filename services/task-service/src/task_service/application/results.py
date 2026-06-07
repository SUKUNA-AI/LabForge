from dataclasses import dataclass

from task_service.domain.task import Task


@dataclass(frozen=True)
class PutTaskResult:
    task: Task
    created: bool
