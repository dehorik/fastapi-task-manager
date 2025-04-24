from typing import Awaitable, Callable
from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from models import Group
from schemas import (
    GroupSchema,
    GroupItemsSchema,
    GroupUsersSchema,
    GroupTasksSchema,
    UserSchema,
    UserPreviewSchema,
    TaskSchema,
    TaskPreviewSchema
)
from .helpers import generate_group_name, generate_group_description
from ..helpers import get_auth_headers


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_group(
        async_client: AsyncClient,
        session: AsyncSession,
        users_factory: Callable[[], Awaitable[UserSchema]]
) -> None:
    user_data = await users_factory()

    headers = get_auth_headers(user_data.user_id)
    json = {
        "name": generate_group_name(),
        "description": generate_group_description()
    }

    response = await async_client.post(
        url="/groups",
        headers=headers,
        json=json
    )
    response_data = response.json()

    await session.execute(
        delete(Group)
        .where(Group.group_id == response_data.get("group_id"))
    )
    await session.commit()

    assert response.status_code == 201
    assert response_data["name"] == json["name"]
    assert response_data["description"] == json["description"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_group(
        async_client: AsyncClient,
        users_factory: Callable[[], Awaitable[UserSchema]],
        groups_factory: Callable[[UUID], Awaitable[GroupSchema]],
        tasks_factory: Callable[[UUID], Awaitable[TaskSchema]]
) -> None:
    """Тест всех конечных точек для получения информации о группе"""

    user_data = await users_factory()
    group_data = await groups_factory(user_data.user_id)
    task_data = await tasks_factory(group_data.group_id)

    user_preview_data = UserPreviewSchema(
        user_id=user_data.user_id,
        username=user_data.username
    )
    task_preview_data = TaskPreviewSchema(
        task_id=task_data.task_id,
        name=task_data.name
    )
    group_items_data = GroupItemsSchema(
        **group_data.model_dump(),
        users=[user_preview_data],
        tasks=[task_preview_data]
    )
    group_users_data = GroupUsersSchema(
        **group_data.model_dump(),
        users=[user_preview_data]
    )
    group_tasks_data = GroupTasksSchema(
        **group_data.model_dump(),
        tasks=[task_preview_data]
    )

    headers = get_auth_headers(user_data.user_id)

    response = await async_client.get(
        url=f"/groups/{group_data.group_id}",
        headers=headers
    )

    assert response.status_code == 200
    assert GroupSchema(**response.json()).model_dump() == group_data.model_dump()

    response = await async_client.get(
        url=f"/groups/{group_data.group_id}/details",
        headers=headers
    )

    assert response.status_code == 200
    assert GroupItemsSchema(**response.json()).model_dump() == group_items_data.model_dump()

    response = await async_client.get(
        url=f"/groups/{group_data.group_id}/users",
        headers=headers
    )

    assert response.status_code == 200
    assert GroupUsersSchema(**response.json()).model_dump() == group_users_data.model_dump()

    response = await async_client.get(
        url=f"/groups/{group_data.group_id}/tasks",
        headers=headers
    )

    assert response.status_code == 200
    assert GroupTasksSchema(**response.json()).model_dump() == group_tasks_data.model_dump()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_group(
        async_client: AsyncClient,
        groups_factory: Callable[[UUID], Awaitable[GroupSchema]],
        users_factory: Callable[[], Awaitable[UserSchema]]
) -> None:
    user_data = await users_factory()
    group_data = await groups_factory(user_data.user_id)

    headers = get_auth_headers(user_data.user_id)
    json = {"name": generate_group_name()}
    group_data.name = json["name"]

    response = await async_client.patch(
        url=f"/groups/{group_data.group_id}",
        headers=headers,
        json=json
    )

    assert response.status_code == 200
    assert GroupSchema(**response.json()).model_dump() == group_data.model_dump()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete(
        async_client: AsyncClient,
        groups_factory: Callable[[UUID], Awaitable[GroupSchema]],
        users_factory: Callable[[], Awaitable[UserSchema]]
) -> None:
    user_data = await users_factory()
    group_data = await groups_factory(user_data.user_id)

    url = f"/groups/{group_data.group_id}"
    headers = get_auth_headers(user_data.user_id)

    response = await async_client.delete(url=url, headers=headers)

    assert response.status_code == 200
    assert GroupSchema(**response.json()).model_dump() == group_data.model_dump()

    response = await async_client.delete(url=url, headers=headers)

    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_add_user_to_group(
        async_client: AsyncClient,
        groups_factory: Callable[[UUID], Awaitable[GroupSchema]],
        users_factory: Callable[[], Awaitable[UserSchema]]
) -> None:
    user_data = await users_factory()
    group_data = await groups_factory(user_data.user_id)

    member_data = await users_factory()

    response = await async_client.post(
        url=f"/groups/{group_data.group_id}/users",
        headers=get_auth_headers(user_data.user_id),
        json={"user_id": str(member_data.user_id)}
    )

    assert response.status_code == 204

    response = await async_client.get(
        url=f"/groups/{group_data.group_id}",
        headers=get_auth_headers(member_data.user_id)
    )

    assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.integration
async def test_remove_user_from_group(
        async_client: AsyncClient,
        groups_factory: Callable[[UUID], Awaitable[GroupSchema]],
        users_factory: Callable[[], Awaitable[UserSchema]],
        users_groups_relations_factory: Callable[[UUID, UUID], Awaitable]
) -> None:
    user_data = await users_factory()
    group_data = await groups_factory(user_data.user_id)

    member_data = await users_factory()
    await users_groups_relations_factory(group_data.group_id, member_data.user_id)

    response = await async_client.delete(
        url=f"/groups/{group_data.group_id}/users/{member_data.user_id}",
        headers=get_auth_headers(user_data.user_id)
    )

    assert response.status_code == 204

    response = await async_client.get(
        url=f"/groups/{group_data.group_id}",
        headers=get_auth_headers(member_data.user_id)
    )

    assert response.status_code == 404
