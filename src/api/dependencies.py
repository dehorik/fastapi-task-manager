from typing import Annotated

from fastapi import Depends

from core import database_helper
from repositories import SQLAlchemyUnitOfWork
from services import UsersService, GroupsService, TasksService


def get_unit_of_work() -> SQLAlchemyUnitOfWork:
    return SQLAlchemyUnitOfWork(database_helper.session_factory)


def get_users_service(
        uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_unit_of_work)]
) -> UsersService:
    return UsersService(uow)


def get_groups_service(
        uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_unit_of_work)]
) -> GroupsService:
    return GroupsService(uow)


def get_tasks_service(
        uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_unit_of_work)]
) -> TasksService:
    return TasksService(uow)
