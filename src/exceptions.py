class ServiceError(Exception):
    pass


class UsersServiceError(ServiceError):
    pass


class UserNotFoundError(UsersServiceError):
    pass


class UsernameTakenError(UsersServiceError):
    pass


class GroupsServiceError(ServiceError):
    pass


class GroupNotFoundError(GroupsServiceError):
    pass


class NonExistentUserError(GroupsServiceError):
    pass


class UserGroupAttachError(GroupsServiceError):
    pass


class UserGroupDetachError(GroupsServiceError):
    pass


class TasksServiceError(ServiceError):
    pass


class TaskNotFoundError(TasksServiceError):
    pass


class NonExistentGroupError(TasksServiceError):
    pass
