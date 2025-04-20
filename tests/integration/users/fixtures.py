import pytest
import pytest_asyncio
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_password_hash
from infrastructure import SQLAlchemyUnitOfWork, UsersRepository
from models import User
from schemas import UserSchema
from services import UsersService
from .helpers import generate_username, generate_password


@pytest.fixture(scope="function")
def users_service(unit_of_work: SQLAlchemyUnitOfWork) -> UsersService:
    return UsersService(unit_of_work)


@pytest.fixture(scope="function")
def users_repository(session: AsyncSession) -> UsersRepository:
    return UsersRepository(session)


@pytest_asyncio.fixture(scope="function")
async def user(session: AsyncSession) -> User:
    """Фикстура для создания тестового пользователя в базе данных"""

    user = User(
        username=generate_username(),
        hashed_password=get_password_hash(generate_password())
    )
    session.add(user)
    await session.commit()
    session.expunge(user)

    return user


@pytest_asyncio.fixture(scope="function")
async def user_data(user: User, session: AsyncSession) -> UserSchema:
    """
    Дополнение к фикстуре user.
    Вернет данные созданного тестового пользователя в виде pydantic схемы,
    авоматически удалит этого пользователя из базы данных по завершении теста
    """

    try:
        user.hashed_password = None
        user_data = UserSchema.model_validate(user, from_attributes=True)
        yield user_data
    finally:
        await session.execute(delete(User).where(User.user_id == user_data.user_id))
        await session.commit()
