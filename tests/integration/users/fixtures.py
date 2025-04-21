import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure import SQLAlchemyUnitOfWork, UsersRepository
from services import UsersService


@pytest.fixture(scope="function")
def users_service(unit_of_work: SQLAlchemyUnitOfWork) -> UsersService:
    return UsersService(unit_of_work)


@pytest.fixture(scope="function")
def users_repository(session: AsyncSession) -> UsersRepository:
    return UsersRepository(session)
