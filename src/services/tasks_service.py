from interfaces import AbstractUnitOfWork


class TasksService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
