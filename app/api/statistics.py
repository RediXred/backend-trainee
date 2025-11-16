from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.base import get_db
from app.schemas.statistics import StatisticsResponse
from app.services.statistics_service import StatisticsService

router = APIRouter()


@router.get(
    "/statistics",
    response_model=StatisticsResponse,
    summary="Получить статистику по PR и назначениям ревьюверов",
    description="Возвращает общую статистику по PR (total, OPEN, MERGED) "
    "и статистику назначений ревьюверов по пользователям",
)
async def get_statistics(db: Session = Depends(get_db)):
    """Получить статистику"""
    return StatisticsService.get_statistics(db)
