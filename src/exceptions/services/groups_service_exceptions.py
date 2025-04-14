from .base_exceptions import ServiceError


class GroupsServiceError(ServiceError):
    """Базовый класс для ошибок сервиса групп задач"""
    pass


class GroupNotFoundError(GroupsServiceError):
    """Бросать, когда группа задач не существует"""
    pass


class UserGroupAttachError(GroupsServiceError):
    """Ошибка добаления пользователя в группу"""
    pass


class UserGroupDetachError(GroupsServiceError):
    """Ошибка удаления пользователя из группы"""
    pass
