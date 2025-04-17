from contextlib import nullcontext
from typing import ContextManager, Any
from unittest.mock import Mock
from uuid import uuid4

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.exc import IntegrityError

from auth.auth_service import AuthService
from auth.exceptions import UsernameTakenError, InvalidCredentialsError
from auth.schemas import CredentialsSchema
from models import User


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["username_is_taken", "expectation"],
    [
        (False, nullcontext()),
        (True, pytest.raises(UsernameTakenError))
    ]
)
async def test_register(
        mocker: MockerFixture,
        fake_uow: Mock,
        fake_credentials_schema: CredentialsSchema,
        username_is_taken: bool,
        expectation: ContextManager[Any]
) -> None:
    mocker.patch("auth.auth_service.get_password_hash", return_value="hash")
    mocker.patch("auth.auth_service.encode_token", return_value="jwt")

    if username_is_taken:
        fake_uow.users.create = mocker.AsyncMock(
            side_effect=IntegrityError(None, None, BaseException())
        )
    else:
        fake_uow.users.create = mocker.AsyncMock(return_value=User(user_id=uuid4()))

    auth_service = AuthService(fake_uow)

    with expectation:
        result = await auth_service.register(fake_credentials_schema)

    fake_uow.users.create.assert_awaited_once_with({
        "username": fake_credentials_schema.username,
        "hashed_password": "hash"
    })
    fake_uow.__aenter__.assert_awaited_once()
    fake_uow.__aexit__.assert_awaited_once()

    if not username_is_taken:
        assert result.model_dump() == {"token": "jwt"}
        fake_uow.commit.assert_awaited_once()
    else:
        fake_uow.commit.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["user_not_found", "password_is_invalid", "expectation"],
    [
        (True, False, pytest.raises(InvalidCredentialsError)),
        (False, True, pytest.raises(InvalidCredentialsError)),
        (False, False, nullcontext())
    ]
)
async def test_login(
        mocker: MockerFixture,
        fake_uow: Mock,
        fake_credentials_schema: CredentialsSchema,
        user_not_found: bool,
        password_is_invalid: bool,
        expectation: ContextManager[Any]
) -> None:
    if user_not_found:
        fake_uow.users.get_user_by_username = mocker.AsyncMock(return_value=None)
    elif password_is_invalid:
        fake_uow.users.get_user_by_username = mocker.AsyncMock(
            return_value=User(hashed_password="hash")
        )

        mocker.patch("auth.auth_service.verify_password", return_value=False)
    else:
        fake_uow.users.get_user_by_username = mocker.AsyncMock(
            return_value=User(hashed_password="hash")
        )

        mocker.patch("auth.auth_service.verify_password", return_value=True)
        mocker.patch("auth.auth_service.encode_token", return_value="jwt")

    auth_service = AuthService(fake_uow)

    with expectation:
        result = await auth_service.login(fake_credentials_schema)

    fake_uow.users.get_user_by_username.assert_awaited_once_with(
        fake_credentials_schema.username
    )
    fake_uow.__aenter__.assert_awaited_once()
    fake_uow.__aexit__.assert_awaited_once()
    fake_uow.commit.assert_not_awaited()

    if not user_not_found and not password_is_invalid:
        assert result.model_dump() == {"token": "jwt"}
