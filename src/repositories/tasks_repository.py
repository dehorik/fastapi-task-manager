from models import Task
from .sqlalchemy_repository import SQLAlchemyRepository


class TasksRepository(SQLAlchemyRepository):
    model = Task
