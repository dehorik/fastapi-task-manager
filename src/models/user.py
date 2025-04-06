from datetime import date
from typing import List
from uuid import uuid4

from sqlalchemy import String, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String(18))
    created_at: Mapped[date] = mapped_column(Date, default=date.today)

    groups: Mapped[List["Group"]] = relationship(
        back_populates="users",
        secondary="users_groups",
        lazy="noload"
    )
