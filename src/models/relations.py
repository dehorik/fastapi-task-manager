from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class UsersGroups(Base):
    __tablename__ = "users_groups"

    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True
    )
    group_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("groups.group_id", ondelete="CASCADE"),
        primary_key=True
    )
