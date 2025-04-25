from typing import AsyncGenerator
from uuid import UUID

import pytest
import pytest_asyncio
from sqlalchemy import delete, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_password_hash
from core import DatabaseHelper
from infrastructure import (
    SQLAlchemyUnitOfWork,
    GroupsRepository,
    TasksRepository,
    UsersRepository
)
from models import User, Group, UsersGroups, Task
from schemas import UserSchema, GroupSchema, TaskSchema
from .groups.helpers import generate_group_name, generate_group_description
from .helpers import generate_username, generate_password
from .tasks.helpers import generate_task_name, generate_task_description


@pytest.fixture(scope="function")
def unit_of_work(database_helper: DatabaseHelper) -> SQLAlchemyUnitOfWork:
    return SQLAlchemyUnitOfWork(
        database_helper.session_factory,
        UsersRepository,
        GroupsRepository,
        TasksRepository
    )


@pytest_asyncio.fixture(scope="function")
async def users_factory(session: AsyncSession) -> AsyncGenerator:
    """
    Фикстура, предоставляющая возможноть создавать временных пользователей
    в базе данных.
    Фикстура предоставляет тесту фабрику, через котрую можно создавать пользователей;
    созданные пользватели будут автоматически удалены из базы данных после теста.

    Использование:
    1) добавить фикстуру в параметры теста
    user_factory: Callable[[], Awaitable[UserSchema]]
    2) эвейтнуть её
    user_data = await users_factory()
    """

    try:
        user_ids = []

        async def create_user() -> UserSchema:
            user = User(
                username=generate_username(),
                hashed_password=get_password_hash(generate_password())
            )
            session.add(user)
            await session.commit()
            session.expunge(user)

            user_ids.append(user.user_id)
            user.hashed_password = None
            user_data = UserSchema.model_validate(user, from_attributes=True)

            return user_data

        yield create_user

    finally:
        if user_ids:
            await session.execute(
                delete(User)
                .where(User.user_id.in_(user_ids))
            )
            await session.commit()


@pytest_asyncio.fixture(scope="function")
async def groups_factory(session: AsyncSession) -> AsyncGenerator:
    """
    Фикстура для создания временных групп в базе данных.
    Возвращает ссылку на фабрику, через которую можно создавать
    неограниченное количество групп на время теста.
    После завершения теста все созданные группы будут удалены из базы данных.

    В фабрику необходимо передать user_id первого участника этой группы
    """

    try:
        group_ids = []

        async def create_group(user_id: UUID) -> GroupSchema:
            group = Group(
                name=generate_group_name(),
                description=generate_group_description()
            )
            session.add(group)
            await session.flush()

            relation = UsersGroups(
                group_id=group.group_id,
                user_id=user_id
            )
            session.add(relation)

            await session.commit()
            session.expunge(group)

            group_ids.append(group.group_id)
            group_data = GroupSchema.model_validate(group, from_attributes=True)

            return group_data

        yield create_group

    finally:
        if group_ids:
            await session.execute(
                delete(Group)
                .where(Group.group_id.in_(group_ids))
            )
            await session.commit()


@pytest_asyncio.fixture(scope="function")
async def users_groups_relations_factory(
        session: AsyncSession
) -> AsyncGenerator:
    """
    Фикстура для добавления пользователя в группу на время теста.
    Требуется существующая группа и существующий пользователь.
    Все созданные связи будут удалены после прогона теста
    """

    try:
        relation_pkeys = []

        async def create_users_groups_relation(
                group_id: UUID,
                user_id: UUID
        ) -> None:
            relation = UsersGroups(
                group_id=group_id,
                user_id=user_id
            )
            session.add(relation)
            await session.commit()
            session.expunge(relation)

            relation_pkeys.append((relation.group_id, relation.user_id))

        yield create_users_groups_relation
    finally:
        if relation_pkeys:
            await session.execute(
                delete(UsersGroups)
                .where(
                    tuple_(UsersGroups.group_id, UsersGroups.user_id)
                    .in_(relation_pkeys)
                )
            )

        await session.commit()


@pytest_asyncio.fixture(scope="function")
async def tasks_factory(session: AsyncSession) -> AsyncGenerator:
    """
    Фикстура для создания временных задач в группе.
    Возвращает фабрику, в котрую требуется передать group_id существующей группы.
    После теста удаляет все созданные с помощью себя задачи
    """

    try:
        task_ids = []

        async def create_task(group_id: UUID) -> TaskSchema:
            task = Task(
                group_id=group_id,
                name=generate_task_name(),
                description=generate_task_description()
            )
            session.add(task)
            await session.commit()
            session.expunge(task)

            task_ids.append(task.task_id)
            task_data = TaskSchema.model_validate(task, from_attributes=True)

            return task_data

        yield create_task

    finally:
        if task_ids:
            await session.execute(
                delete(Task)
                .where(Task.task_id.in_(task_ids))
            )
            await session.commit()
