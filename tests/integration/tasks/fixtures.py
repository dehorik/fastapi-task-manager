import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure import SQLAlchemyUnitOfWork, TasksRepository
from services import TasksService


@pytest.fixture(scope="function")
def tasks_service(unit_of_work: SQLAlchemyUnitOfWork) -> TasksService:
    return TasksService(unit_of_work)


@pytest.fixture(scope="function")
def tasks_repository(session: AsyncSession) -> TasksRepository:
    return TasksRepository(session)
