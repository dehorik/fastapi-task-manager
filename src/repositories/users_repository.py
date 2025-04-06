from sqlalchemy import select

from models import User
from .sqlalchemy_repository import SQLAlchemyRepository


class UsersRepository(SQLAlchemyRepository):
    model = User

    async def get_by_username(self, username: str) -> User:
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one()
