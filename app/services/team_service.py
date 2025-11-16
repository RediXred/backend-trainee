from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Team, User
from app.schemas.error import ErrorDetail, ErrorResponse
from app.schemas.team import TeamCreate


class TeamService:
    @staticmethod
    def create_team(db: Session, team_data: TeamCreate) -> Team:
        """Создать команду с участниками"""
        existing_team = db.query(Team).filter(Team.team_name == team_data.team_name).first()
        if existing_team:
            error_response = ErrorResponse(
                error=ErrorDetail(code="TEAM_EXISTS", message="team_name already exists")
            )
            raise HTTPException(status_code=400, detail=error_response.model_dump())

        team = Team(team_name=team_data.team_name)
        db.add(team)
        for member_data in team_data.members:
            user = db.query(User).filter(User.user_id == member_data.user_id).first()
            if user:
                user.username = member_data.username
                user.team_name = team_data.team_name
                user.is_active = member_data.is_active
            else:
                user = User(
                    user_id=member_data.user_id,
                    username=member_data.username,
                    team_name=team_data.team_name,
                    is_active=member_data.is_active,
                )
                db.add(user)

        try:
            db.commit()
            db.refresh(team)
            return team
        except IntegrityError:
            db.rollback()
            error_response = ErrorResponse(
                error=ErrorDetail(code="TEAM_EXISTS", message="team_name already exists")
            )
            raise HTTPException(status_code=400, detail=error_response.model_dump())

    @staticmethod
    def get_team(db: Session, team_name: str) -> Team:
        """Получить команду с участниками"""
        team = db.query(Team).filter(Team.team_name == team_name).first()
        if not team:
            error_response = ErrorResponse(
                error=ErrorDetail(code="NOT_FOUND", message="resource not found")
            )
            raise HTTPException(status_code=404, detail=error_response.model_dump())
        return team
