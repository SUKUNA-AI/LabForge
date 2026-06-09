class TaskApplicationError(Exception):
    pass


class TaskNotFound(TaskApplicationError):
    pass


class TaskAlreadyExists(TaskApplicationError):
    pass


class TaskConflict(TaskApplicationError):
    pass
