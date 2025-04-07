from datetime import date
from typing import List
from uuid import uuid4

from sqlalchemy import String, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Group(Base):
    __tablename__ = "groups"

    group_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[date] = mapped_column(Date, default=date.today)

    users: Mapped[List["User"]] = relationship(
        back_populates="groups",
        secondary="users_groups",
        lazy="noload"
    )

    tasks: Mapped[List["Task"]] = relationship(
        back_populates="group",
        lazy="noload"
    )
