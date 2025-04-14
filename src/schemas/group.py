from datetime import date
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field

from .task import TaskPreviewSchema
from .user import UserPreviewSchema


class GroupSchema(BaseModel):
    """Схема данных группы задач"""

    group_id: UUID
    name: str
    description: str
    created_at: date


class GroupPreviewSchema(BaseModel):
    """Схема данных группы задач для предпросмотра"""

    group_id: UUID
    name: str


class GroupPreviewListSchema(BaseModel):
    """Схема данных списка из групп задач"""

    groups: List[GroupPreviewSchema]


class GroupItemsSchema(GroupSchema):
    """Схема данных со всей информацией, связанной с группой"""

    users: List[UserPreviewSchema]
    tasks: List[TaskPreviewSchema]


class GroupUsersSchema(GroupSchema):
    """
    Схема данных группы задач
    + идентифицирующая информация об участниках группы
    """

    users: List[UserPreviewSchema]


class GroupTasksSchema(GroupSchema):
    """
    Схема данных группы задач
    + идентифицирующая информация о задачах, принадлежащих этой группе
    """

    tasks: List[TaskPreviewSchema]


class GroupSchemaCreate(BaseModel):
    """Тело запроса на создание группы задач"""

    name: str = Field(max_length=50)
    description: str = Field(max_length=200)


class GroupSchemaUpdate(BaseModel):
    """Тело запроса на обновление данных группы задач"""

    name: str | None = Field(max_length=50, default=None)
    description: str | None = Field(max_length=200, default=None)


class UserGroupSchemaAttach(BaseModel):
    """Тело запроса на добавление участника в группу"""

    user_id: UUID
