from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class UserSchema(BaseModel):
    user_id: UUID
    username: str
    created_at: date


class UserPreviewSchema(BaseModel):
    user_id: UUID
    username: str


class UserSchemaCreate(BaseModel):
    username: str = Field(min_length=4, max_length=18)


class UserSchemaUpdate(BaseModel):
    username: str = Field(min_length=4, max_length=18)
