from typing import Awaitable, Callable
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from schemas import UserSchema
from .helpers import generate_username
from ..helpers import get_auth_headers


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    ["user_not_found"],
    [
        (False,), (True,)
    ]
)
async def test_get_user(
        async_client: AsyncClient,
        users_factory: Callable[[], Awaitable[UserSchema]],
        user_not_found: bool
) -> None:
    user_data = await users_factory()

    url = "/users/me"
    headers = get_auth_headers(uuid4() if user_not_found else user_data.user_id)

    response = await async_client.get(url=url, headers=headers)

    if user_not_found:
        assert response.status_code == 404
    else:
        assert response.status_code == 200
        assert UserSchema(**response.json()).model_dump() == user_data.model_dump()


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    ["user_not_found", "username_is_taken"],
    [
        (False, False),
        (True, False),
        (False, True)
    ]
)
async def test_update_user(
        async_client: AsyncClient,
        session: AsyncSession,
        users_factory: Callable[[], Awaitable[UserSchema]],
        user_not_found: bool,
        username_is_taken: bool
) -> None:
    user_data = await users_factory()

    if user_not_found:
        json = {}
    elif username_is_taken:
        new_user_data = await users_factory()
        json = {"username": new_user_data.username}
    else:
        json = {"username": generate_username()}
        user_data.username = json["username"]

    url = "/users/me"
    headers = get_auth_headers(uuid4() if user_not_found else user_data.user_id)

    response = await async_client.patch(url=url, headers=headers, json=json)

    if user_not_found:
        assert response.status_code == 404
    elif username_is_taken:
        assert response.status_code == 409
    else:
        assert response.status_code == 200
        assert UserSchema(**response.json()).model_dump() == user_data.model_dump()


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    ["user_not_found"],
    [
        (False,), (True,)
    ]
)
async def test_delete_user(
        async_client: AsyncClient,
        users_factory: Callable[[], Awaitable[UserSchema]],
        user_not_found: bool
) -> None:
    user_data = await users_factory()

    url = "/users/me"
    headers = get_auth_headers(uuid4() if user_not_found else user_data.user_id)

    response = await async_client.delete(
        url=url,
        headers=headers
    )

    if user_not_found:
        assert response.status_code == 404
    else:
        assert response.status_code == 200
        assert UserSchema(**response.json()).model_dump() == user_data.model_dump()

        response = await async_client.delete(url=url, headers=headers)
        assert response.status_code == 404
