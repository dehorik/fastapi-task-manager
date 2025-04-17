from typing import Annotated

from fastapi import Depends

from core import database_helper
from infrastructure import (
    SQLAlchemyUnitOfWork,
    UsersRepository,
    TasksRepository,
    GroupsRepository
)
from interfaces import AbstractUnitOfWork
from services import UsersService, GroupsService, TasksService


def get_unit_of_work() -> AbstractUnitOfWork:
    return SQLAlchemyUnitOfWork(
        database_helper.session_factory,
        UsersRepository,
        GroupsRepository,
        TasksRepository
    )


def get_users_service(
        uow: Annotated[AbstractUnitOfWork, Depends(get_unit_of_work)]
) -> UsersService:
    return UsersService(uow)


def get_groups_service(
        uow: Annotated[AbstractUnitOfWork, Depends(get_unit_of_work)]
) -> GroupsService:
    return GroupsService(uow)


def get_tasks_service(
        uow: Annotated[AbstractUnitOfWork, Depends(get_unit_of_work)]
) -> TasksService:
    return TasksService(uow)
