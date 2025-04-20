from datetime import date
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.exc import IntegrityError

from auth import TokenPayloadSchema
from exceptions import ResultNotFound, UserNotFoundError, UsernameTakenError
from models import User
from schemas import UserSchema, UserSchemaUpdate
from services import UsersService


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_user(
        mocker: MockerFixture,
        fake_uow: Mock,
        fake_token_payload: TokenPayloadSchema
) -> None:
    fake_user_schema = UserSchema(
        user_id=fake_token_payload.sub,
        username="egor",
        created_at=date.today()
    )
    fake_user_model = User(
        user_id=fake_token_payload.sub,
        username=fake_user_schema.username,
        hashed_password=None,
        created_at=fake_user_schema.created_at
    )

    fake_uow.users.get = mocker.AsyncMock(return_value=fake_user_model)

    users_service = UsersService(fake_uow)

    result = await users_service.get_user(fake_token_payload)
    assert result.model_dump() == fake_user_schema.model_dump()

    fake_uow.users.get.assert_awaited_once_with(fake_token_payload.sub)
    fake_uow.__aenter__.assert_awaited_once()
    fake_uow.__aexit__.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_non_existent_user(
        mocker: MockerFixture,
        fake_uow: Mock,
        fake_token_payload: TokenPayloadSchema
) -> None:
    fake_uow.users.get = mocker.AsyncMock(return_value=None)

    users_service = UsersService(fake_uow)

    with pytest.raises(UserNotFoundError):
        await users_service.get_user(fake_token_payload)

    fake_uow.users.get.assert_awaited_once_with(fake_token_payload.sub)
    fake_uow.__aenter__.assert_awaited_once()
    fake_uow.__aexit__.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_full_update_user(
        mocker: MockerFixture,
        fake_uow: Mock,
        fake_token_payload: TokenPayloadSchema,
        fake_user_schema_update: UserSchemaUpdate
) -> None:
    fake_user_schema = UserSchema(
        user_id=fake_token_payload.sub,
        username=fake_user_schema_update.username,
        created_at=date.today()
    )
    fake_user_model = User(
        user_id=fake_token_payload.sub,
        username=fake_user_schema_update.username,
        hashed_password=None,
        created_at=fake_user_schema.created_at
    )

    mocker.patch("services.users_service.get_password_hash", return_value="hash")
    fake_uow.users.update = mocker.AsyncMock(return_value=fake_user_model)

    users_service = UsersService(fake_uow)

    result = await users_service.update_user(
        fake_token_payload,
        fake_user_schema_update
    )
    assert result.model_dump() == fake_user_schema.model_dump()

    fake_uow.users.update.assert_awaited_once_with(
        fake_token_payload.sub,
        {
            "username": fake_user_schema_update.username,
            "hashed_password": "hash"
        }
    )
    fake_uow.__aenter__.assert_awaited_once()
    fake_uow.__aexit__.assert_awaited_once()
    fake_uow.commit.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_partial_update_user(
        mocker: MockerFixture,
        fake_uow: Mock,
        fake_token_payload: TokenPayloadSchema
) -> None:
    fake_user_schema_update = UserSchemaUpdate(
        username="egor",
        password=None
    )
    fake_user_schema = UserSchema(
        user_id=fake_token_payload.sub,
        username="egor",
        created_at=date.today()
    )
    fake_user_model = User(
        user_id=fake_token_payload.sub,
        username=fake_user_schema.username,
        hashed_password=None,
        created_at=fake_user_schema.created_at
    )

    fake_uow.users.update = mocker.AsyncMock(return_value=fake_user_model)

    users_service = UsersService(fake_uow)

    result = await users_service.update_user(
        fake_token_payload,
        fake_user_schema_update
    )
    assert result.model_dump() == fake_user_schema.model_dump()

    fake_uow.users.update.assert_awaited_once_with(
        fake_token_payload.sub,
        {"username": fake_user_schema_update.username}
    )
    fake_uow.__aenter__.assert_awaited_once()
    fake_uow.__aexit__.assert_awaited_once()
    fake_uow.commit.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_non_existent_user(
        mocker: MockerFixture,
        fake_uow: Mock,
        fake_token_payload: TokenPayloadSchema,
        fake_user_schema_update: UserSchemaUpdate
) -> None:
    fake_uow.users.update = mocker.AsyncMock(side_effect=ResultNotFound())

    users_service = UsersService(fake_uow)

    with pytest.raises(UserNotFoundError):
        await users_service.update_user(fake_token_payload, fake_user_schema_update)

    fake_uow.__aenter__.assert_awaited_once()
    fake_uow.__aexit__.assert_awaited_once()
    fake_uow.commit.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_user_with_taken_username(
        mocker: MockerFixture,
        fake_uow: Mock,
        fake_token_payload: TokenPayloadSchema,
        fake_user_schema_update: UserSchemaUpdate
) -> None:
    fake_uow.users.update = mocker.AsyncMock(
        side_effect=IntegrityError(None, None, BaseException())
    )

    users_service = UsersService(fake_uow)

    with pytest.raises(UsernameTakenError):
        await users_service.update_user(fake_token_payload, fake_user_schema_update)

    fake_uow.__aenter__.assert_awaited_once()
    fake_uow.__aexit__.assert_awaited_once()
    fake_uow.commit.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_delete_user(
        mocker: MockerFixture,
        fake_uow: Mock,
        fake_token_payload: TokenPayloadSchema
) -> None:
    fake_user_schema = UserSchema(
        user_id=fake_token_payload.sub,
        username="egor",
        created_at=date.today()
    )
    fake_user_model = User(
        user_id=fake_token_payload.sub,
        username=fake_user_schema.username,
        hashed_password=None,
        created_at=fake_user_schema.created_at
    )

    fake_uow.users.delete = mocker.AsyncMock(return_value=fake_user_model)

    users_service = UsersService(fake_uow)

    result = await users_service.delete_user(fake_token_payload)
    assert result.model_dump() == fake_user_schema.model_dump()

    fake_uow.users.delete.assert_awaited_once_with(fake_token_payload.sub)
    fake_uow.__aenter__.assert_awaited_once()
    fake_uow.__aexit__.assert_awaited_once()
    fake_uow.commit.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_delete_non_existent_user(
        mocker: MockerFixture,
        fake_uow: Mock,
        fake_token_payload: TokenPayloadSchema
) -> None:
    fake_uow.users.delete = mocker.AsyncMock(side_effect=ResultNotFound())

    users_service = UsersService(fake_uow)

    with pytest.raises(UserNotFoundError):
        await users_service.delete_user(fake_token_payload)

    fake_uow.__aenter__.assert_awaited_once()
    fake_uow.__aexit__.assert_awaited_once()
    fake_uow.commit.assert_not_awaited()
