from sqlalchemy.ext.asyncio import async_sessionmaker

from interfaces import AbstractUnitOfWork
from .groups_repository import GroupsRepository
from .tasks_repository import TasksRepository
from .users_repository import UsersRepository


class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory: async_sessionmaker):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()

        self.users = UsersRepository(self.session)
        self.groups = GroupsRepository(self.session)
        self.tasks = TasksRepository(self.session)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()

        await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
