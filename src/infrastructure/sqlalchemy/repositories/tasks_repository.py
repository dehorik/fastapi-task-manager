from models import Task
from .sqlalchemy_repository import SQLAlchemyRepository


class TasksRepository(SQLAlchemyRepository):
    """Реализация репозитория для работы с задачами"""

    model = Task
