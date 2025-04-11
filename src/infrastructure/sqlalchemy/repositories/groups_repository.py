from typing import Dict, Any, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload, load_only

from exceptions import ResultNotFound
from models import Group, UsersGroups, User, Task
from .sqlalchemy_repository import SQLAlchemyRepository


class GroupsRepository(SQLAlchemyRepository):
    """Реализация репозитория для работы с группами задач"""

    model = Group

    async def create(self, data: Dict[str, Any]) -> Group:
        group = Group(name=data["name"], description=data["description"])
        self.session.add(group)
        await self.session.flush()

        relation = UsersGroups(group_id=group.group_id, user_id=data["user_id"])
        self.session.add(relation)

        return group

    async def get_group_details(self, group_id: UUID) -> Group:
        """Получение данных о группе + все relationship"""

        group = await self.session.execute(
            select(Group)
            .where(Group.group_id == group_id)
            .options(
                selectinload(Group.users).load_only(User.user_id, User.username),
                selectinload(Group.tasks).load_only(Task.task_id, Task.name)
            )
        )
        return group.scalar_one_or_none()

    async def get_group_users(self, group_id: UUID) -> Group:
        """Получение данных о группе + relationship с User"""

        group = await self.session.execute(
            select(Group)
            .options(selectinload(Group.users).load_only(User.user_id, User.username))
            .where(Group.group_id == group_id)
        )
        return group.scalar_one_or_none()

    async def get_group_tasks(self, group_id: UUID) -> Group:
        """Получение данных о группе + relationship с Task"""

        group = await self.session.execute(
            select(Group)
            .options(selectinload(Group.tasks).load_only(Task.task_id, Task.name))
            .where(Group.group_id == group_id)
        )
        return group.scalar_one_or_none()

    async def get_user_groups_list(self, user_id: UUID) -> List[Group]:
        """
        Получение только group_id и name для каждой группы,
        которая связана с переданным user_id
        """

        groups = await self.session.execute(
            select(Group)
            .options(load_only(Group.group_id, Group.name))
            .join(UsersGroups)
            .join(User)
            .where(User.user_id == user_id)
        )
        return list(groups.scalars().all())

    async def add_user_to_group(self, group_id: UUID, user_id: UUID) -> None:
        relation = UsersGroups(group_id=group_id, user_id=user_id)
        self.session.add(relation)

    async def remove_user_from_group(self, group_id: UUID, user_id: UUID) -> None:
        relation = await self.session.get(UsersGroups, [group_id, user_id])

        if relation is None:
            raise ResultNotFound("relation not found")

        await self.session.delete(relation)
