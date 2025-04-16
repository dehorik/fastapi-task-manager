from datetime import datetime, UTC, date
from typing import Tuple
from unittest.mock import Mock
from uuid import uuid4, UUID

import pytest
from pytest_mock import MockerFixture

from auth import TokenPayloadSchema
from models import Task
from schemas import UserSchemaUpdate, TaskSchema


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


@pytest.fixture(scope="function")
def fake_user_schema_update() -> UserSchemaUpdate:
    return UserSchemaUpdate(
        username="egor",
        password="11111111"
    )


def make_fake_task(
        task_id: UUID | None = None,
        group_id: UUID | None = None,
        name: str = "task",
        description: str = "task",
        created_at: date = None,
        estimated_time: int = 1
) -> Tuple[TaskSchema, Task]:
    """
    Генерация тестовых данных для задачи.
    Используется для моков, проверки возвратов
    и передачи в тестируемые функции

    :return:
    TaskSchema - pydantic-схема задачи
    Task - ORM-модель задачи
    """

    task_id = task_id or uuid4()
    group_id = group_id or uuid4()
    created_at = created_at or date.today()

    fake_task_schema = TaskSchema(
        task_id=task_id,
        group_id=group_id,
        name=name,
        description=description,
        created_at=created_at,
        estimated_time=estimated_time
    )
    fake_task_model = Task(**fake_task_schema.model_dump())

    return fake_task_schema, fake_task_model
