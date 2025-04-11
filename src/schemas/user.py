from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class UserSchema(BaseModel):
    """Схема данных пользователя"""

    user_id: UUID
    username: str
    created_at: date


class UserPreviewSchema(BaseModel):
    """Схема данных пользователя только с идентифицирующими полями"""

    user_id: UUID
    username: str


class UserSchemaCreate(BaseModel):
    """Тело запроса на создание пользователя"""

    username: str = Field(min_length=4, max_length=18)


class UserSchemaUpdate(BaseModel):
    """Тело запроса на обновление пользователя"""

    username: str = Field(min_length=4, max_length=18)
