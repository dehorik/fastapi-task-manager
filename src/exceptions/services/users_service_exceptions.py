from .base_exceptions import ServiceError


class UsersServiceError(ServiceError):
    """Базовый класс для ошибок сервиса пользователей"""
    pass


class UserNotFoundError(UsersServiceError):
    """Ошибка, когда пользователь не существует"""
    pass


class UsernameTakenError(UsersServiceError):
    """Ошибка, когда username уже занят"""
    pass
