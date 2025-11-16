from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.base import get_db
from app.schemas.error import ErrorResponse
from app.schemas.team import TeamCreate, TeamCreateResponse, TeamResponse
from app.services.team_service import TeamService

router = APIRouter()


@router.post(
    "/team/add",
    status_code=status.HTTP_201_CREATED,
    response_model=TeamCreateResponse,
    responses={
        201: {"description": "Команда создана"},
        400: {"model": ErrorResponse, "description": "Команда уже существует"},
    },
)
async def create_team(team_data: TeamCreate, db: Session = Depends(get_db)):
    """Создать команду с участниками (создаёт/обновляет пользователей)"""
    team = TeamService.create_team(db, team_data)
    team_response = TeamResponse.model_validate(team)
    return TeamCreateResponse(team=team_response)


@router.get(
    "/team/get",
    response_model=TeamResponse,
    responses={
        200: {"description": "Объект команды"},
        404: {"model": ErrorResponse, "description": "Команда не найдена"},
    },
)
async def get_team(
    team_name: str = Query(..., description="Уникальное имя команды"),
    db: Session = Depends(get_db),
):
    """Получить команду с участниками"""
    team = TeamService.get_team(db, team_name)
    return TeamResponse.model_validate(team)
