import pytest

from schemas import UserSchema, UserSchemaUpdate
from services.users_service import UsersService
from .helpers import generate_username
from ..helpers import get_fake_token_payload


@pytest.mark.asyncio
async def test_get_user(
        users_service: UsersService,
        user_data: UserSchema
) -> None:
    payload = get_fake_token_payload(user_data.user_id)

    user = await users_service.get_user(payload)
    assert user.model_dump() == user_data.model_dump()


@pytest.mark.asyncio
async def test_update_user(
        users_service: UsersService,
        user_data: UserSchema
) -> None:
    paylaod = get_fake_token_payload(user_data.user_id)
    user_schema_update = UserSchemaUpdate(username=generate_username())
    user_data.username = user_schema_update.username

    user = await users_service.update_user(paylaod, user_schema_update)
    assert user.model_dump() == user_data.model_dump()


@pytest.mark.asyncio
async def test_delete_user(
        users_service: UsersService,
        user_data: UserSchema
) -> None:
    payload = get_fake_token_payload(user_data.user_id)

    user = await users_service.delete_user(payload)
    assert user.model_dump() == user_data.model_dump()
