from models import Group
from .sqlalchemy_repository import SQLAlchemyRepository


class GroupsRepository(SQLAlchemyRepository):
    model = Group
