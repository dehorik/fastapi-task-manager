class ServiceError(Exception):
    pass


class UsersServiceError(ServiceError):
    pass


class UserNotFoundError(UsersServiceError):
    pass
