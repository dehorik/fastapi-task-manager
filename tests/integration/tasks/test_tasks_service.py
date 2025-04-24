from contextlib import nullcontext
from random import choice, randint
from typing import Awaitable, Callable, Any, ContextManager
from uuid import UUID, uuid4

import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import NonExistentGroupError, TaskNotFoundError
from models import Task
from schemas import (
    TaskSchema,
    TaskSchemaCreate,
    TaskSchemaUpdate,
    UserSchema,
    GroupSchema
)
from services import TasksService
from .helpers import generate_task_name, generate_task_description
from ..helpers import get_fake_token_payload


@pytest.mark.asyncio
@pytest.mark.integration
async def test_check_user_access_to_task(
        tasks_service: TasksService,
        tasks_factory: Callable[[UUID], Awaitable[TaskSchema]],
        users_factory: Callable[[], Awaitable[UserSchema]],
        groups_factory: Callable[[UUID], Awaitable[GroupSchema]],
        users_groups_relations_factory: Callable[[UUID, UUID], Awaitable]
) -> None:
    members_data = [await users_factory() for _ in range(randint(2, 4))]
    users_data = [await users_factory() for _ in range(randint(2, 4))]

    group_data = await groups_factory(members_data[0].user_id)

    for member_data in members_data[1:]:
        await users_groups_relations_factory(
            group_data.group_id,
            member_data.user_id
        )

    task_data = await tasks_factory(group_data.group_id)

    async with tasks_service.uow as uow:
        for member_data in members_data:
            assert await tasks_service._check_user_access_to_task(
                uow,
                member_data.user_id,
                task_data.task_id
            )

        for user_data in users_data:
            assert not await tasks_service._check_user_access_to_task(
                uow,
                user_data.user_id,
                task_data.task_id
            )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    ["group_not_found", "user_not_in_group", "expectation"],
    [
        (False, False, nullcontext()),
        (True, False, pytest.raises(NonExistentGroupError)),
        (False, True, pytest.raises(NonExistentGroupError))
    ]
)
async def test_create_task(
        session: AsyncSession,
        tasks_service: TasksService,
        users_factory: Callable[[], Awaitable[UserSchema]],
        groups_factory: Callable[[UUID], Awaitable[GroupSchema]],
        group_not_found: bool,
        user_not_in_group: bool,
        expectation: ContextManager[Any]
) -> None:
    user_data = await users_factory()
    group_data = await groups_factory(user_data.user_id)

    if user_not_in_group:
        payload = get_fake_token_payload(uuid4())
    else:
        payload = get_fake_token_payload(user_data.user_id)

    task_schema_create = TaskSchemaCreate(
        group_id=(uuid4() if group_not_found else group_data.group_id),
        name=generate_task_name(),
        description=generate_task_description(),
        estimated_time=choice([None, 1, 2])
    )

    with expectation:
        task = await tasks_service.create_task(payload, task_schema_create)

    if not group_not_found and not user_not_in_group:
        await session.execute(delete(Task).where(Task.task_id == task.task_id))
        await session.commit()

        assert task.name == task_schema_create.name
        assert task.description == task_schema_create.description
        assert task.estimated_time == task_schema_create.estimated_time


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    ["task_not_found", "user_not_in_group", "expectation"],
    [
        (False, False, nullcontext()),
        (True, False, pytest.raises(TaskNotFoundError)),
        (False, True, pytest.raises(TaskNotFoundError))
    ]
)
async def test_get_task(
        tasks_service: TasksService,
        tasks_factory: Callable[[UUID], Awaitable[TaskSchema]],
        users_factory: Callable[[], Awaitable[UserSchema]],
        groups_factory: Callable[[UUID], Awaitable[GroupSchema]],
        task_not_found: bool,
        user_not_in_group: bool,
        expectation: ContextManager[Any]
) -> None:
    user_data = await users_factory()
    group_data = await groups_factory(user_data.user_id)
    task_data = await tasks_factory(group_data.group_id)

    task_id = uuid4() if task_not_found else task_data.task_id

    if user_not_in_group:
        payload = get_fake_token_payload(uuid4())
    else:
        payload = get_fake_token_payload(user_data.user_id)

    with expectation:
        task = await tasks_service.get_task(payload, task_id)

    if not task_not_found and not user_not_in_group:
        assert task.model_dump() == task_data.model_dump()


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    ["task_not_found", "user_not_in_group", "expectation"],
    [
        (False, False, nullcontext()),
        (True, False, pytest.raises(TaskNotFoundError)),
        (False, True, pytest.raises(TaskNotFoundError))
    ]
)
async def test_update_task(
        tasks_service: TasksService,
        tasks_factory: Callable[[UUID], Awaitable[TaskSchema]],
        users_factory: Callable[[], Awaitable[UserSchema]],
        groups_factory: Callable[[UUID], Awaitable[GroupSchema]],
        task_not_found: bool,
        user_not_in_group: bool,
        expectation: ContextManager[Any]
) -> None:
    user_data = await users_factory()
    group_data = await groups_factory(user_data.user_id)
    task_data = await tasks_factory(group_data.group_id)

    task_id = uuid4() if task_not_found else task_data.task_id

    if user_not_in_group:
        payload = get_fake_token_payload(uuid4())
    else:
        payload = get_fake_token_payload(user_data.user_id)

    task_schema_update = TaskSchemaUpdate(
        name=generate_task_name(),
        description=generate_task_description(),
        estimated_time=choice([1, 2, 3])
    )
    task_data.name = task_schema_update.name
    task_data.description = task_schema_update.description
    task_data.estimated_time = task_schema_update.estimated_time

    with expectation:
        task = await tasks_service.update_task(
            payload,
            task_id,
            task_schema_update
        )

    if not task_not_found and not user_not_in_group:
        assert task.model_dump() == task_data.model_dump()

        task_schema_update = TaskSchemaUpdate(
            description=generate_task_description()
        )
        task_data.description = task_schema_update.description

        task = await tasks_service.update_task(
            payload,
            task_id,
            task_schema_update
        )

        assert task.model_dump() == task_data.model_dump()


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    ["task_not_found", "user_not_in_group", "expectation"],
    [
        (False, False, nullcontext()),
        (True, False, pytest.raises(TaskNotFoundError)),
        (False, True, pytest.raises(TaskNotFoundError))
    ]
)
async def test_delete_task(
        tasks_service: TasksService,
        tasks_factory: Callable[[UUID], Awaitable[TaskSchema]],
        users_factory: Callable[[], Awaitable[UserSchema]],
        groups_factory: Callable[[UUID], Awaitable[GroupSchema]],
        task_not_found: bool,
        user_not_in_group: bool,
        expectation: ContextManager[Any]
) -> None:
    user_data = await users_factory()
    group_data = await groups_factory(user_data.user_id)
    task_data = await tasks_factory(group_data.group_id)

    task_id = uuid4() if task_not_found else task_data.task_id

    if user_not_in_group:
        payload = get_fake_token_payload(uuid4())
    else:
        payload = get_fake_token_payload(user_data.user_id)

    with expectation:
        task = await tasks_service.delete_task(payload, task_id)

    if not task_not_found and not user_not_in_group:
        assert task.model_dump() == task_data.model_dump()

        with pytest.raises(TaskNotFoundError):
            await tasks_service.delete_task(payload, task_id)
