from datetime import date
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field

from .task import TaskSchema
from .user import UserSchema


class GroupSchema(BaseModel):
    group_id: UUID
    name: str
    description: str
    created_at: date


class GroupItemsSchema(GroupSchema):
    users: List[UserSchema]
    tasks: List[TaskSchema]


class GroupSchemaCreate(BaseModel):
    user_id: UUID
    name: str = Field(max_length=50)
    description: str = Field(max_length=200)


class GroupSchemaUpdate(BaseModel):
    name: str | None = Field(max_length=50, default=None)
    description: str | None = Field(max_length=200, default=None)


class UserGroupSchemaAttach(BaseModel):
    user_id: UUID
