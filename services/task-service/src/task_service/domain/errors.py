class TaskDomainError(Exception):
    pass


class InvalidTaskTitle(TaskDomainError):
    pass


class InvalidTaskStatus(TaskDomainError):
    pass


class InvalidTaskPriority(TaskDomainError):
    pass


class InvalidTaskSourceType(TaskDomainError):
    pass


class InvalidTaskStatusTransition(TaskDomainError):
    pass