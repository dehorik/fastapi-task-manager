from datetime import datetime, timedelta, UTC
from typing import Awaitable, Callable
from uuid import uuid4

import jwt
import pytest
from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_password_hash
from core import settings
from models import User
from schemas import UserSchema
from ..helpers import generate_username, generate_password, get_auth_headers


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    ["username_is_taken"],
    [
        (False,), (True,)
    ]
)
async def test_register(
        async_client: AsyncClient,
        session: AsyncSession,
        users_factory: Callable[[], Awaitable[UserSchema]],
        username_is_taken: bool
) -> None:
    if username_is_taken:
        user_data = await users_factory()

        json = {
            "username": user_data.username,
            "password": generate_password()
        }
    else:
        json = {
            "username": generate_username(),
            "password": generate_password()
        }

    try:
        response = await async_client.post(url="/auth/register", json=json)

        if username_is_taken:
            assert response.status_code == 409
        else:
            assert response.status_code == 201

            response = await async_client.get(
                url="/users/me",
                headers={"Authorization": f"Bearer {response.json()["token"]}"}
            )

            assert response.status_code == 200
            assert response.json()["username"] == json["username"]
    finally:
        if not username_is_taken:
            await session.execute(
                delete(User)
                .where(User.username == json["username"])
            )
            await session.commit()


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    ["username_is_invalid", "password_is_invalid"],
    [
        (False, False),
        (True, False),
        (False, True)
    ]
)
async def test_login(
        async_client: AsyncClient,
        session: AsyncSession,
        username_is_invalid,
        password_is_invalid
) -> None:
    username = generate_username()
    row_password = generate_password()
    hashed_password = get_password_hash(row_password)

    user = User(
        username=username,
        hashed_password=hashed_password
    )
    session.add(user)
    await session.commit()
    session.expunge(user)

    json = {
        "username": (generate_username() if username_is_invalid else username),
        "password": (generate_password() if password_is_invalid else row_password)
    }

    try:
        response = await async_client.post(url="/auth/login", json=json)

        if username_is_invalid or password_is_invalid:
            assert response.status_code == 401
        else:
            assert response.status_code == 200

            response = await async_client.get(
                url="/users/me",
                headers={"Authorization": f"Bearer {response.json()["token"]}"}
            )

            assert response.status_code == 200
            assert response.json()["username"] == json["username"]
    finally:
        await session.execute(
            delete(User)
            .where(User.username == user.username)
        )
        await session.commit()


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    ["signature_is_invalid", "token_is_expired"],
    [
        (False, False),
        (True, False),
        (False, True)
    ]
)
async def test_refresh(
        async_client: AsyncClient,
        users_factory: Callable[[], Awaitable[UserSchema]],
        signature_is_invalid: bool,
        token_is_expired: bool
) -> None:
    user_data = await users_factory()

    iat = datetime.now(UTC)
    exp = iat + timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES)
    key = settings.TOKEN_SECRET_KEY

    if token_is_expired:
        exp = iat - timedelta(seconds=1)
    if signature_is_invalid:
        key = "super_secret_fake_key"

    payload = {
        "sub": str(user_data.user_id),
        "iat": iat,
        "exp": exp
    }

    token = jwt.encode(payload, key=key, algorithm=settings.ALGORITHM)

    response = await async_client.post(
        url="/auth/refresh",
        headers={"Authorization": f"Bearer {token}"}
    )

    if signature_is_invalid or token_is_expired:
        assert response.status_code == 401
    else:
        assert response.status_code == 200

        response = await async_client.get(
            url="/users/me",
            headers={"Authorization": f"Bearer {response.json()["token"]}"}
        )

        assert response.status_code == 200
        assert response.json()["user_id"] == str(user_data.user_id)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_logout(async_client: AsyncClient) -> None:
    response = await async_client.post(
        url="/auth/logout",
        headers=get_auth_headers(uuid4())
    )
    assert response.status_code == 204
