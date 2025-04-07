from typing import Dict, Any
from uuid import UUID

from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from interfaces import AbstractRepository
from models import Base


class SQLAlchemyRepository(AbstractRepository):
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, data: Dict[str, Any]) -> Base:
        model = self.model(**data)
        self.session.add(model)
        return model

    async def get(self, model_id: UUID) -> Base:
        model = await self.session.get(self.model, model_id)
        return model

    async def update(self, model_id: UUID, data: Dict[str, Any]) -> Base:
        model = await self.session.get(self.model, model_id)

        if model is None:
            raise NoResultFound(f"model with model_id={model_id} not found")

        for key, value in data.items():
            setattr(model, key, value)

        return model

    async def remove(self, model_id: UUID) -> Base:
        model = await self.session.get(self.model, model_id)

        if model is None:
            raise NoResultFound(f"model with model_id={model_id} not found")

        await self.session.delete(model)
        return model
