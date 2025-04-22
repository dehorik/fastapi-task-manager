import pytest

from infrastructure import SQLAlchemyUnitOfWork
from services import GroupsService


@pytest.fixture(scope="function")
def groups_service(unit_of_work: SQLAlchemyUnitOfWork) -> GroupsService:
    return GroupsService(unit_of_work)
