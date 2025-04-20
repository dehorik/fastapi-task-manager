import pytest

from core import DatabaseHelper
from infrastructure import (
    SQLAlchemyUnitOfWork,
    GroupsRepository,
    TasksRepository,
    UsersRepository
)


@pytest.fixture(scope="function")
def unit_of_work(database_helper: DatabaseHelper) -> SQLAlchemyUnitOfWork:
    return SQLAlchemyUnitOfWork(
        database_helper.session_factory,
        UsersRepository,
        GroupsRepository,
        TasksRepository
    )
