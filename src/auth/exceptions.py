class AuthServiceError(Exception):
    """Базовый класс для всех ошибок сервиса аутентификации"""
    pass


class InvalidCredentialsError(AuthServiceError):
    """Ошибка, когда были переданы невалидные данные для входа в аккаунт"""
    pass


class UsernameTakenError(AuthServiceError):
    """Ошибка, когда username уже занят"""
    pass
