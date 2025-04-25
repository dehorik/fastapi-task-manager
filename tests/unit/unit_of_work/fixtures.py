import pytest
from pytest_mock import MockerFixture

from infrastructure import SQLAlchemyUnitOfWork


@pytest.fixture(scope="function")
def uow(mocker: MockerFixture) -> SQLAlchemyUnitOfWork:
    """
    Фикстура для получения готового к тестам объекта SQLAlchemyUnitOfWork
    (все зависимости от сессии алхимии мокнуты)
    """

    fake_session = mocker.Mock()
    fake_session.commit = mocker.AsyncMock()
    fake_session.rollback = mocker.AsyncMock()
    fake_session.close = mocker.AsyncMock()

    fake_users_repository = mocker.Mock(session=fake_session)
    fake_groups_repository = mocker.Mock(session=fake_session)
    fake_tasks_repository = mocker.Mock(session=fake_session)

    fake_session_factory = mocker.Mock(return_value=fake_session)
    fake_users_repository_factory = mocker.Mock(return_value=fake_users_repository)
    fake_groups_repository_factory = mocker.Mock(return_value=fake_groups_repository)
    fake_tasks_repository_factory = mocker.Mock(return_value=fake_tasks_repository)

    return SQLAlchemyUnitOfWork(
        fake_session_factory,
        fake_users_repository_factory,
        fake_groups_repository_factory,
        fake_tasks_repository_factory
    )
