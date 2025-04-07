from typing import Dict, Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import selectinload

from models import Group, UsersGroups
from .sqlalchemy_repository import SQLAlchemyRepository


class GroupsRepository(SQLAlchemyRepository):
    model = Group

    async def create(self, data: Dict[str, Any]) -> Group:
        group = Group(name=data["name"], description=data["description"])
        self.session.add(group)
        await self.session.flush()

        relation = UsersGroups(group_id=group.group_id, user_id=data["user_id"])
        self.session.add(relation)

        return group

    async def get_full_data(self, group_id: UUID) -> Group:
        stmt = (
            select(Group)
            .where(Group.group_id == group_id)
            .options(selectinload(Group.users))
            .options(selectinload(Group.tasks))
        )
        group = await self.session.execute(stmt)
        return group.scalar_one_or_none()

    async def add_user(self, group_id: UUID, user_id: UUID) -> None:
        relation = UsersGroups(group_id=group_id, user_id=user_id)
        self.session.add(relation)

    async def remove_user(self, group_id: UUID, user_id: UUID) -> None:
        relation = await self.session.get(UsersGroups, [group_id, user_id])

        if relation is None:
            raise NoResultFound("there is no such relation")

        await self.session.delete(relation)
