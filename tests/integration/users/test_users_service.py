from contextlib import nullcontext
from typing import ContextManager, Any
from uuid import uuid4

import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_password_hash
from exceptions import UserNotFoundError, UsernameTakenError
from models import User
from schemas import UserSchema, UserSchemaUpdate
from services.users_service import UsersService
from .helpers import generate_username, generate_password
from ..helpers import get_fake_token_payload


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    ["user_not_found", "expectation"],
    [
        (False, nullcontext()),
        (True, pytest.raises(UserNotFoundError))
    ]
)
async def test_get_user(
        users_service: UsersService,
        user_data: UserSchema,
        user_not_found: bool,
        expectation: ContextManager[Any]
) -> None:
    if user_not_found:
        payload = get_fake_token_payload(uuid4())
    else:
        payload = get_fake_token_payload(user_data.user_id)

    with expectation:
        user = await users_service.get_user(payload)

    if not user_not_found:
        assert user.model_dump() == user_data.model_dump()


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    ["user_not_found", "username_is_taken", "expectation"],
    [
        (False, False, nullcontext()),
        (True, False, pytest.raises(UserNotFoundError)),
        (False, True, pytest.raises(UsernameTakenError))
    ]
)
async def test_update_user(
        users_service: UsersService,
        session: AsyncSession,
        user_data: UserSchema,
        user_not_found: bool,
        username_is_taken: bool,
        expectation: ContextManager[Any]
) -> None:
    try:
        if user_not_found:
            payload = get_fake_token_payload(uuid4())
            user_schema_update = UserSchemaUpdate()
        elif username_is_taken:
            new_user = User(
                username=generate_username(),
                hashed_password=get_password_hash(generate_password())
            )
            session.add(new_user)
            await session.commit()
            session.expunge(new_user)

            new_user.hashed_password = None
            new_user_data = UserSchema.model_validate(new_user, from_attributes=True)

            payload = get_fake_token_payload(user_data.user_id)
            user_schema_update = UserSchemaUpdate(username=new_user_data.username)
        else:
            payload = get_fake_token_payload(user_data.user_id)
            user_schema_update = UserSchemaUpdate(username=generate_username())
            user_data.username = user_schema_update.username

        with expectation:
            user = await users_service.update_user(payload, user_schema_update)

        if not user_not_found and not username_is_taken:
            assert user.model_dump() == user_data.model_dump()
    finally:
        if username_is_taken:
            await session.execute(
                delete(User)
                .where(User.user_id == new_user_data.user_id)
            )
            await session.commit()


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    ["user_not_found", "expectation"],
    [
        (False, nullcontext()),
        (True, pytest.raises(UserNotFoundError))
    ]
)
async def test_delete_user(
        users_service: UsersService,
        user_data: UserSchema,
        user_not_found: bool,
        expectation: ContextManager[Any]
) -> None:
    if user_not_found:
        payload = get_fake_token_payload(uuid4())
    else:
        payload = get_fake_token_payload(user_data.user_id)

    with expectation:
        user = await users_service.delete_user(payload)

    if not user_not_found:
        assert user.model_dump() == user_data.model_dump()

        with pytest.raises(UserNotFoundError):
            await users_service.delete_user(payload)
