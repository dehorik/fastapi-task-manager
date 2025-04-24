from random import randint
from typing import Callable, Awaitable
from uuid import UUID

import pytest

from infrastructure import TasksRepository
from schemas import UserSchema, GroupSchema, TaskSchema


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_task_id_if_user_in_group(
        tasks_repository: TasksRepository,
        tasks_factory: Callable[[UUID], Awaitable[TaskSchema]],
        users_factory: Callable[[], Awaitable[UserSchema]],
        groups_factory: Callable[[UUID], Awaitable[GroupSchema]],
        users_groups_relations_factory: Callable[[UUID, UUID], Awaitable]
) -> None:
    members_data = [await users_factory() for _ in range(randint(2, 4))]
    users_data = [await users_factory() for _ in range(randint(2, 4))]

    group_data = await groups_factory(members_data[0].user_id)

    task_data = await tasks_factory(group_data.group_id)

    for member_data in members_data[1:]:
        await users_groups_relations_factory(
            group_data.group_id,
            member_data.user_id
        )

    for member_data in members_data:
        assert await tasks_repository.get_task_id_if_user_in_group(
            member_data.user_id,
            task_data.task_id
        ) == task_data.task_id

    for user_data in users_data:
        assert await tasks_repository.get_task_id_if_user_in_group(
            user_data.user_id,
            task_data.task_id
        ) is None
