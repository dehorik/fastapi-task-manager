from datetime import date
from typing import List
from uuid import uuid4

from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Task(Base):
    __tablename__ = "tasks"

    task_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    group_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("groups.group_id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[date] = mapped_column(default=date.today)
    estimated_time: Mapped[int | None]

    group: Mapped[List["Group"]] = relationship(back_populates="tasks", lazy="noload")
