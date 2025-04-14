from typing import Dict, Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import load_only

from exceptions import ResultNotFound
from models import User
from .sqlalchemy_repository import SQLAlchemyRepository


class UsersRepository(SQLAlchemyRepository):
    """Реализация репозитория для работы с пользователями"""

    model = User

    async def get(self, user_id: UUID) -> User:
        """Получение данных пользователя (кроме хеша пароля)"""

        user = await self.session.execute(
            select(User)
            .options(load_only(User.user_id, User.username, User.created_at))
            .where(User.user_id == user_id)
        )
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User:
        """Получение данных пользователя вместе с хешом пароля"""

        user = await self.session.execute(
            select(User)
            .where(User.username == username)
        )
        return user.scalar_one_or_none()

    async def update(self, user_id: UUID, data: Dict[str, Any]) -> User:
        """
        Обновление данных пользователя;
        Метод поднимет исключение ResultNotFound, если пользователь
        с переданным user_id не будет существовать. Так было сделано для
        сохранения совместимости с базовым классом SQLAlchemyRepository,
        метод update которого поднимает исключение, если запись в БД не существует
        """

        user = await self.session.get(
            User,
            user_id,
            options=[load_only(User.user_id, User.username, User.created_at)]
        )

        if user is None:
            raise ResultNotFound("user not found")

        for key, value in data.items():
            setattr(user, key, value)

        return user

    async def delete(self, user_id: UUID) -> User:
        """
        Удаление пользователя;
        Метод поднимет исключение ResultNotFound, если пользователь
        с переданным user_id не будет существовать. Так было сделано для
        сохранения совместимости с базовым классом SQLAlchemyRepository,
        метод delete которого поднимает исключение, если запись в БД не существует
        """

        user = await self.session.get(
            User,
            user_id,
            options=[load_only(User.user_id, User.username, User.created_at)]
        )

        if user is None:
            raise ResultNotFound("user not found")

        await self.session.delete(user)

        return user
