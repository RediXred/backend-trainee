from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from .user import User


class Team(Base):
    """Модель команды"""

    __tablename__ = "teams"

    team_name: Mapped[str] = mapped_column(String, primary_key=True)
    members: Mapped[list["User"]] = relationship(
        "User", back_populates="team", cascade="all, delete-orphan"
    )
