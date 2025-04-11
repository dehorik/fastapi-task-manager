from models import User
from .sqlalchemy_repository import SQLAlchemyRepository


class UsersRepository(SQLAlchemyRepository):
    """Реализация репозитория для работы с пользователями"""

    model = User
