from datetime import datetime, UTC
from unittest.mock import Mock
from uuid import uuid4

import pytest
from pytest_mock import MockerFixture

from auth import TokenPayloadSchema


@pytest.fixture(scope="function")
def fake_uow(mocker: MockerFixture) -> Mock:
    fake_uow = mocker.Mock()
    fake_uow.__aenter__ = mocker.AsyncMock(return_value=fake_uow)
    fake_uow.__aexit__ = mocker.AsyncMock(return_value=None)
    fake_uow.commit = mocker.AsyncMock(return_value=None)
    fake_uow.rollback = mocker.AsyncMock(return_value=None)

    return fake_uow


@pytest.fixture(scope="function")
def fake_token_payload() -> TokenPayloadSchema:
    return TokenPayloadSchema(
        sub=uuid4(),
        iat=datetime.now(UTC),
        exp=datetime.now(UTC),
    )
