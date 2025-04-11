from .base_exceptions import ServiceError


class TasksServiceError(ServiceError):
    """Базовый класс для ошибок сервиса задач"""
    pass


class TaskNotFoundError(TasksServiceError):
    """Ошибка, когда задача не существует"""


class NonExistentGroupError(TasksServiceError):
    """Ошибка, когда задача создается в несущетсвующей группе"""
    pass
