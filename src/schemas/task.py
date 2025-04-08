from datetime import date
from uuid import UUID

from pydantic import BaseModel


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
