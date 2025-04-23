from random import randint
from typing import Callable, Awaitable
from uuid import UUID

import pytest

from infrastructure import GroupsRepository
from models import Group
from schemas import UserSchema, GroupSchema, TaskSchema
from .helpers import generate_group_name, generate_group_description


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create(
        groups_repository: GroupsRepository,
        users_factory: Callable[[], Awaitable[UserSchema]]
) -> None:
    try:
        user_data = await users_factory()

        group_data_dict = {
            "user_id": user_data.user_id,
            "name": generate_group_name(),
            "description": generate_group_description()
        }

        group = await groups_repository.create(group_data_dict)
        await groups_repository.session.flush()
        groups_repository.session.expunge(group)
        assert group.name == group_data_dict["name"]

        group = await groups_repository.session.get(Group, group.group_id)
        assert group.name == group_data_dict["name"]
    finally:
        await groups_repository.session.rollback()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_group(
        groups_repository: GroupsRepository,
        groups_factory: Callable[[UUID], Awaitable[GroupSchema]],
        users_factory: Callable[[], Awaitable[UserSchema]],
        users_groups_relations_factory: Callable[[UUID, UUID], Awaitable],
        tasks_factory: Callable[[UUID], Awaitable[TaskSchema]]
) -> None:
    """
    Тестирует методы для получения информации о группе.

    Тестируемые методы:
    SQLAlchemyRepository.get
    GroupsRepository.get_group_details
    GroupsRepository.get_group_users
    GroupsRepository.get_group_tasks
    """

    users_data = [
        await users_factory()
        for _ in range(randint(2, 4))
    ]

    group_data = await groups_factory(users_data[0].user_id)

    for user_data in users_data[1:]:
        await users_groups_relations_factory(
            group_data.group_id,
            user_data.user_id
        )

    tasks_data = [
        await tasks_factory(group_data.group_id)
        for _ in range(randint(2, 4))
    ]

    group_basic = await groups_repository.get(group_data.group_id)
    groups_repository.session.expunge_all()

    assert group_basic
    assert group_basic.group_id == group_data.group_id
    assert group_basic.name == group_data.name

    group_details = await groups_repository.get_group_details(group_data.group_id)
    groups_repository.session.expunge_all()

    assert group_details
    assert group_details.group_id == group_data.group_id
    assert group_details.name == group_data.name
    assert len(group_details.users) == len(users_data)
    assert len(group_details.tasks) == len(tasks_data)

    group_users = await groups_repository.get_group_users(group_data.group_id)
    groups_repository.session.expunge_all()

    assert group_users
    assert group_users.group_id == group_data.group_id
    assert group_users.name == group_data.name
    assert len(group_users.users) == len(users_data)

    group_tasks = await groups_repository.get_group_tasks(group_data.group_id)
    groups_repository.session.expunge_all()

    assert group_tasks
    assert group_tasks.group_id == group_data.group_id
    assert group_tasks.name == group_data.name
    assert len(group_tasks.tasks) == len(tasks_data)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_user_groups_list(
        groups_repository: GroupsRepository,
        groups_factory: Callable[[UUID], Awaitable[GroupSchema]],
        users_factory: Callable[[], Awaitable[UserSchema]]
) -> None:
    user_data = await users_factory()

    groups_data = [
        await groups_factory(user_data.user_id)
        for _ in range(randint(2, 4))
    ]

    groups_list = await groups_repository.get_user_groups_list(user_data.user_id)

    assert len(groups_list) == len(groups_data)


@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_get_group_id_if_user_in_group(
        groups_repository: GroupsRepository,
        groups_factory: Callable[[UUID], Awaitable[GroupSchema]],
        users_factory: Callable[[], Awaitable[UserSchema]],
        users_groups_relations_factory: Callable[[UUID, UUID], Awaitable]
) -> None:
    users_data = [
        await users_factory()
        for _ in range(2, 4)
    ]

    members_data = [
        await users_factory()
        for _ in range(2, 4)
    ]

    group_data = await groups_factory(members_data[0].user_id)

    for member_data in members_data[1:]:
        await users_groups_relations_factory(
            group_data.group_id,
            member_data.user_id
        )

    for member_data in members_data:
        assert await groups_repository.get_group_id_if_user_in_group(
            member_data.user_id,
            group_data.group_id
        )

    for user_data in users_data:
        assert not await groups_repository.get_group_id_if_user_in_group(
            user_data.user_id,
            group_data.group_id
        )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_add_user_to_group(
        groups_repository: GroupsRepository,
        groups_factory: Callable[[UUID], Awaitable[GroupSchema]],
        users_factory: Callable[[], Awaitable[UserSchema]]
) -> None:
    members_data = [
        await users_factory()
        for _ in range(randint(2, 4))
    ]

    group_data = await groups_factory(members_data[0].user_id)

    for member_data in members_data[1:]:
        await groups_repository.add_user_to_group(
            group_data.group_id,
            member_data.user_id
        )

    await groups_repository.session.flush()
    groups_repository.session.expire_all()

    for member_data in members_data:
        assert await groups_repository.get_group_id_if_user_in_group(
            member_data.user_id,
            group_data.group_id
        )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_remove_user_from_group(
        groups_repository: GroupsRepository,
        groups_factory: Callable[[UUID], Awaitable[GroupSchema]],
        users_factory: Callable[[], Awaitable[UserSchema]],
        users_groups_relations_factory: Callable[[UUID, UUID], Awaitable]
) -> None:
    members_data = [
        await users_factory()
        for _ in range(randint(2, 4))
    ]

    group_data = await groups_factory(members_data[0].user_id)

    for member_data in members_data[1:]:
        await users_groups_relations_factory(
            group_data.group_id,
            member_data.user_id
        )

    for member_data in members_data:
        await groups_repository.remove_user_from_group(
            group_data.group_id,
            member_data.user_id
        )

    await groups_repository.session.flush()
    groups_repository.session.expire_all()

    for member_data in members_data:
        assert not await groups_repository.get_group_id_if_user_in_group(
            member_data.user_id,
            group_data.group_id
        )
