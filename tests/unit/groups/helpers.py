from datetime import date
from typing import Tuple
from uuid import UUID, uuid4

from models import Group
from schemas import GroupSchema


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
