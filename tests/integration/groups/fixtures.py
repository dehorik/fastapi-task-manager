import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure import SQLAlchemyUnitOfWork, GroupsRepository
from services import GroupsService


@pytest.fixture(scope="function")
def groups_service(unit_of_work: SQLAlchemyUnitOfWork) -> GroupsService:
    return GroupsService(unit_of_work)


@pytest.fixture(scope="function")
def groups_repository(session: AsyncSession) -> GroupsRepository:
    return GroupsRepository(session)
