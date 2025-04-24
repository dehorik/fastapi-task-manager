from typing import Callable, Awaitable
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from models import Task
from schemas import TaskSchema, UserSchema, GroupSchema
from .helpers import generate_task_name, generate_task_description
from ..helpers import get_auth_headers


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    ["group_not_found", "user_not_in_group"],
    [
        (False, False),
        (True, False),
        (False, True)
    ]
)
async def test_create_task(
        async_client: AsyncClient,
        session: AsyncSession,
        users_factory: Callable[[], Awaitable[UserSchema]],
        groups_factory: Callable[[UUID], Awaitable[GroupSchema]],
        group_not_found: bool,
        user_not_in_group: bool
) -> None:
    user_data = await users_factory()
    group_data = await groups_factory(user_data.user_id)

    headers = get_auth_headers(uuid4() if user_not_in_group else user_data.user_id)

    json = {
        "group_id": str(uuid4()) if group_not_found else str(group_data.group_id),
        "name": generate_task_name(),
        "description": generate_task_description()
    }

    response = await async_client.post(url="/tasks", headers=headers, json=json)

    if not group_not_found and not user_not_in_group:
        response_data = response.json()

        await session.execute(
            delete(Task)
            .where(Task.task_id == response_data["task_id"])
        )
        await session.commit()

        assert response.status_code == 201
        assert response_data["name"] == json["name"]
        assert response_data["description"] == json["description"]
    else:
        assert response.status_code == 400


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    ["task_not_found", "user_not_in_group"],
    [
        (False, False),
        (True, False),
        (False, True)
    ]
)
async def test_get_task(
        async_client: AsyncClient,
        tasks_factory: Callable[[UUID], Awaitable[TaskSchema]],
        users_factory: Callable[[], Awaitable[UserSchema]],
        groups_factory: Callable[[UUID], Awaitable[GroupSchema]],
        task_not_found: bool,
        user_not_in_group: bool
) -> None:
    user_data = await users_factory()
    group_data = await groups_factory(user_data.user_id)
    task_data = await tasks_factory(group_data.group_id)

    url = f"/tasks/{uuid4() if task_not_found else task_data.task_id}"
    headers = get_auth_headers(uuid4() if user_not_in_group else user_data.user_id)

    response = await async_client.get(url=url, headers=headers)

    if not task_not_found and not user_not_in_group:
        assert response.status_code == 200
        assert TaskSchema(**response.json()).model_dump() == task_data.model_dump()
    else:
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    ["task_not_found", "user_not_in_group"],
    [
        (False, False),
        (True, False),
        (False, True)
    ]
)
async def test_update_task(
        async_client: AsyncClient,
        tasks_factory: Callable[[UUID], Awaitable[TaskSchema]],
        users_factory: Callable[[], Awaitable[UserSchema]],
        groups_factory: Callable[[UUID], Awaitable[GroupSchema]],
        task_not_found: bool,
        user_not_in_group: bool
) -> None:
    user_data = await users_factory()
    group_data = await groups_factory(user_data.user_id)
    task_data = await tasks_factory(group_data.group_id)

    url = f"/tasks/{uuid4() if task_not_found else task_data.task_id}"
    headers = get_auth_headers(uuid4() if user_not_in_group else user_data.user_id)

    json = {"name": generate_task_name()}
    task_data.name = json["name"]

    response = await async_client.patch(url=url, headers=headers, json=json)

    if not task_not_found and not user_not_in_group:
        assert response.status_code == 200
        assert TaskSchema(**response.json()).model_dump() == task_data.model_dump()
    else:
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    ["task_not_found", "user_not_in_group"],
    [
        (False, False),
        (True, False),
        (False, True)
    ]
)
async def test_delete_task(
        async_client: AsyncClient,
        tasks_factory: Callable[[UUID], Awaitable[TaskSchema]],
        users_factory: Callable[[], Awaitable[UserSchema]],
        groups_factory: Callable[[UUID], Awaitable[GroupSchema]],
        task_not_found: bool,
        user_not_in_group: bool
) -> None:
    user_data = await users_factory()
    group_data = await groups_factory(user_data.user_id)
    task_data = await tasks_factory(group_data.group_id)

    url = f"/tasks/{uuid4() if task_not_found else task_data.task_id}"
    headers = get_auth_headers(uuid4() if user_not_in_group else user_data.user_id)

    response = await async_client.delete(url=url, headers=headers)

    if not task_not_found and not user_not_in_group:
        assert response.status_code == 200
        assert TaskSchema(**response.json()).model_dump() == task_data.model_dump()

        response = await async_client.delete(url=url, headers=headers)
        assert response.status_code == 404
    else:
        assert response.status_code == 404
