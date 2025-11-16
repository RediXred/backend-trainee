import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.base import Base

if TYPE_CHECKING:
    from .user import User


class PRStatus(str, enum.Enum):
    """Статус PR"""

    OPEN = "OPEN"
    MERGED = "MERGED"


class PullRequest(Base):
    """Модель PR"""

    __tablename__ = "pull_requests"

    pull_request_id: Mapped[str] = mapped_column(String, primary_key=True)
    pull_request_name: Mapped[str] = mapped_column(String, nullable=False)
    author_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[PRStatus] = mapped_column(
        SQLEnum(PRStatus), nullable=False, default=PRStatus.OPEN, index=True
    )
    assigned_reviewers: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    merged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    author: Mapped["User"] = relationship(
        "User", foreign_keys=[author_id], back_populates="authored_prs"
    )
