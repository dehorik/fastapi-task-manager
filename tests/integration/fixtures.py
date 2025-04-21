from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_password_hash
from core import DatabaseHelper
from infrastructure import (
    SQLAlchemyUnitOfWork,
    GroupsRepository,
    TasksRepository,
    UsersRepository
)
from models import User
from schemas import UserSchema
from .users.helpers import generate_username, generate_password


@pytest.fixture(scope="function")
def unit_of_work(database_helper: DatabaseHelper) -> SQLAlchemyUnitOfWork:
    return SQLAlchemyUnitOfWork(
        database_helper.session_factory,
        UsersRepository,
        GroupsRepository,
        TasksRepository
    )


@pytest_asyncio.fixture(scope="function")
async def users_factory(session: AsyncSession) -> AsyncGenerator:
    """
    Фикстура, предоставляющая возможноть создавать временных пользователей
    в базе данных.
    Фикстура предоставляет тесту фабрику, через котрую можно создавать пользователей;
    созданные пользватели будут автоматически удалены из базы данных после теста.

    Использование:
    1) добавить фикстуру в параметры теста
    user_factory: Callable[[], Awaitable[UserSchema]]
    2) эвейтнуть её
    user_data = await users_factory()
    """

    try:
        user_ids = []

        async def create_user() -> UserSchema:
            user = User(
                username=generate_username(),
                hashed_password=get_password_hash(generate_password())
            )
            session.add(user)
            await session.commit()
            session.expunge(user)

            user_ids.append(user.user_id)
            user.hashed_password = None
            user_data = UserSchema.model_validate(user, from_attributes=True)

            return user_data

        yield create_user

    finally:
        if user_ids:
            await session.execute(
                delete(User)
                .where(User.user_id.in_(user_ids))
            )
            await session.commit()
