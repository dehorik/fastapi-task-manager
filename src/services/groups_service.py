from interfaces import AbstractUnitOfWork


class GroupsService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
