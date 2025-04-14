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


class UserSchemaUpdate(BaseModel):
    """Тело запроса на обновление пользователя"""

    username: str | None = Field(min_length=4, max_length=18, default=None)
    password: str | None = Field(min_length=8, max_length=18, default=None)
