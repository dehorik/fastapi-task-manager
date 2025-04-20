from contextlib import nullcontext
from typing import ContextManager, Any

import pytest
from pytest_mock import MockerFixture

from infrastructure import SQLAlchemyUnitOfWork


@pytest.mark.asyncio
@pytest.mark.unit
async def test_aenter(mocker: MockerFixture) -> None:
    fake_session = mocker.Mock()
    fake_session.rollback = mocker.AsyncMock()
    fake_session.close = mocker.AsyncMock()

    fake_users_repository = mocker.Mock()
    fake_groups_repository = mocker.Mock()
    fake_tasks_repository = mocker.Mock()

    fake_session_factory = mocker.Mock(return_value=fake_session)
    fake_users_repository_factory = mocker.Mock(return_value=fake_users_repository)
    fake_groups_repository_factory = mocker.Mock(return_value=fake_groups_repository)
    fake_tasks_repository_factory = mocker.Mock(return_value=fake_tasks_repository)

    uow = SQLAlchemyUnitOfWork(
        fake_session_factory,
        fake_users_repository_factory,
        fake_groups_repository_factory,
        fake_tasks_repository_factory
    )

    async with uow as _uow:
        session = _uow.session
        assert session is fake_session

        assert _uow.users is fake_users_repository
        assert _uow.groups is fake_groups_repository
        assert _uow.tasks is fake_tasks_repository

        assert uow is _uow

    fake_session_factory.assert_called_once()
    fake_users_repository_factory.assert_called_once_with(fake_session)
    fake_groups_repository_factory.assert_called_once_with(fake_session)
    fake_tasks_repository_factory.assert_called_once_with(fake_session)


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.parametrize(
    ["raise_exception", "expectation"],
    [
        (True, pytest.raises(Exception)),
        (False, nullcontext())
    ]
)
async def test_aexit(
        uow: SQLAlchemyUnitOfWork,
        raise_exception: bool,
        expectation: ContextManager[Any]
) -> None:
    with expectation:
        async with uow as _uow:
            session = _uow.session

            if raise_exception:
                raise Exception

    session.commit.assert_not_awaited()
    session.close.assert_awaited_once()

    assert uow.session is None
    assert uow.users is None
    assert uow.groups is None
    assert uow.tasks is None

    if raise_exception:
        session.rollback.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_commit(uow: SQLAlchemyUnitOfWork) -> None:
    async with uow as _uow:
        session = _uow.session
        await _uow.commit()

    session.commit.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_rollback(uow: SQLAlchemyUnitOfWork) -> None:
    async with uow as _uow:
        session = _uow.session
        await _uow.rollback()

    session.rollback.assert_awaited_once()
    session.commit.assert_not_awaited()
