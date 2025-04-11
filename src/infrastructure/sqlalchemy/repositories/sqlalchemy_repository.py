from typing import Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import ResultNotFound
from interfaces import AbstractRepository
from models import Base


class SQLAlchemyRepository(AbstractRepository):
    """Реализация репозитория под SQLAlchemy"""

    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: Dict[str, Any]) -> Base:
        entity = self.model(**data)
        self.session.add(entity)
        return entity

    async def get(self, entity_id: UUID) -> Base:
        entity = await self.session.get(self.model, entity_id)
        return entity

    async def update(self, entity_id: UUID, data: Dict[str, Any]) -> Base:
        entity = await self.session.get(self.model, entity_id)

        if entity is None:
            raise ResultNotFound("result not found")

        for key, value in data.items():
            setattr(entity, key, value)

        return entity

    async def delete(self, entity_id: UUID) -> Base:
        entity = await self.session.get(self.model, entity_id)

        if entity is None:
            raise ResultNotFound("result not found")

        await self.session.delete(entity)
        return entity
