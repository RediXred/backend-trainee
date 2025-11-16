from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .team import Team
    from .pull_request import PullRequest

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class User(Base):
    """Модель пользователя"""

    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=False)
    team_name: Mapped[str] = mapped_column(
        String, ForeignKey("teams.team_name", ondelete="CASCADE"), nullable=False, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    team: Mapped["Team"] = relationship("Team", back_populates="members")
    authored_prs: Mapped[list["PullRequest"]] = relationship(
        "PullRequest", foreign_keys="PullRequest.author_id", back_populates="author"
    )
