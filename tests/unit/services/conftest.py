from datetime import date
from typing import Tuple
from uuid import uuid4, UUID

import pytest

from models import Task, Group
from schemas import UserSchemaUpdate, TaskSchema, GroupSchema


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


def make_fake_group(
        group_id: UUID | None = None,
        name: str = "group",
        description: str = "group",
        created_at: date | None = None
) -> Tuple[GroupSchema, Group]:
    """
    Генерация тестовых данных для группы.
    Используется для моков, проверки возвратов
    и передачи в тестируемые функции

    :return:
    GroupSchema - pydantic-схема группы
    Group - ORM-модель группы
    """

    group_id = group_id or uuid4()
    created_at = created_at or date.today()

    fake_group_schema = GroupSchema(
        group_id=group_id,
        name=name,
        description=description,
        created_at=created_at
    )
    fake_group_model = Group(**fake_group_schema.model_dump())

    return fake_group_schema, fake_group_model
