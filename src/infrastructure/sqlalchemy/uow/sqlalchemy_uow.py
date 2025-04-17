from typing import Type

from sqlalchemy.ext.asyncio import async_sessionmaker

from interfaces import AbstractUnitOfWork
from ..repositories import UsersRepository, GroupsRepository, TasksRepository


class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    """Реализация Unit of Work для репозиториев, использующих SQLAlchemy"""

    def __init__(
            self,
            session_factory: async_sessionmaker,
            users_repository_factory: Type[UsersRepository],
            groups_repository_factory: Type[GroupsRepository],
            tasks_repository_factory: Type[TasksRepository]
    ):
        self.__session_factory = session_factory
        self.__users_repository_factory = users_repository_factory
        self.__groups_repository_factory = groups_repository_factory
        self.__tasks_repository_factory = tasks_repository_factory

    async def __aenter__(self):
        self.session = self.__session_factory()

        self.users = self.__users_repository_factory(self.session)
        self.groups = self.__groups_repository_factory(self.session)
        self.tasks = self.__tasks_repository_factory(self.session)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()

        await self.session.close()
        self.session = None

        self.users = None
        self.groups = None
        self.tasks = None

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
