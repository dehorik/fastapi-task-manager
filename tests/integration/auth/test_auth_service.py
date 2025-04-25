from contextlib import nullcontext
from typing import Awaitable, Callable, Any, ContextManager

import jwt
import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth_service import AuthService
from auth.exceptions import UsernameTakenError, InvalidCredentialsError
from auth.hashing import get_password_hash
from auth.schemas import CredentialsSchema
from core import settings
from models import User
from schemas import UserSchema
from ..helpers import generate_password, generate_username


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    ["username_is_taken", "expectation"],
    [
        (False, nullcontext()),
        (True, pytest.raises(UsernameTakenError))
    ]
)
async def test_register(
        auth_service: AuthService,
        session: AsyncSession,
        users_factory: Callable[[], Awaitable[UserSchema]],
        username_is_taken: bool,
        expectation: ContextManager[Any]
) -> None:
    if username_is_taken:
        user_data = await users_factory()

        credentials_schema = CredentialsSchema(
            username=user_data.username,
            password=generate_password()
        )
    else:
        credentials_schema = CredentialsSchema(
            username=generate_username(),
            password=generate_password()
        )

    try:
        with expectation:
            token = await auth_service.register(credentials_schema)

        if not username_is_taken:
            jwt.decode(
                jwt=token.token,
                key=settings.TOKEN_SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )

            with pytest.raises(UsernameTakenError):
                await auth_service.register(credentials_schema)
    finally:
        if not username_is_taken:
            await session.execute(
                delete(User)
                .where(User.username == credentials_schema.username)
            )
            await session.commit()


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    ["username_is_invalid", "password_is_invalid", "expectation"],
    [
        (False, False, nullcontext()),
        (True, False, pytest.raises(InvalidCredentialsError)),
        (False, True, pytest.raises(InvalidCredentialsError))
    ]
)
async def test_login(
        auth_service: AuthService,
        session: AsyncSession,
        username_is_invalid: bool,
        password_is_invalid: bool,
        expectation: ContextManager[Any]
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

    credentials_schema = CredentialsSchema(
        username=(generate_username() if username_is_invalid else username),
        password=(generate_password() if password_is_invalid else row_password)
    )

    try:
        with expectation:
            token = await auth_service.login(credentials_schema)

        if not username_is_invalid and not password_is_invalid:
            jwt.decode(
                token.token,
                key=settings.TOKEN_SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
    finally:
        await session.execute(
            delete(User)
            .where(User.username == user.username)
        )
        await session.commit()
