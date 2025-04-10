from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class TaskSchema(BaseModel):
    task_id: UUID
    group_id: UUID
    name: str
    description: str
    created_at: date
    estimated_time: int


class TaskPreviewSchema(BaseModel):
    task_id: UUID
    name: str


class TaskSchemaCreate(BaseModel):
    group_id: UUID
    name: str = Field(max_length=50)
    description: str = Field(max_length=100)
    estimated_time: int


class TaskSchemaUpdate(BaseModel):
    name: str | None = Field(max_length=50, default=None)
    description: str | None = Field(max_length=100, default=None)
    estimated_time: int | None
