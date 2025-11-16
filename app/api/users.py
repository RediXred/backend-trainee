from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.base import get_db
from app.schemas.error import ErrorResponse
from app.schemas.pull_request import PullRequestShort
from app.schemas.user import (
    BulkDeactivateRequest,
    BulkDeactivateResponse,
    SetIsActiveRequest,
    UserResponse,
    UserReviewResponse,
    UserSetIsActiveResponse,
)
from app.services.user_service import UserService

router = APIRouter()


@router.post(
    "/users/setIsActive",
    response_model=UserSetIsActiveResponse,
    responses={
        200: {"description": "Обновлённый пользователь"},
        404: {"model": ErrorResponse, "description": "Пользователь не найден"},
    },
)
async def set_is_active(request: SetIsActiveRequest, db: Session = Depends(get_db)):
    """
    Установить флаг активности пользователя
    (при деактивации автоматически переназначаются ревьюверы в открытых PR)
    """
    user, reassigned_count = UserService.set_is_active(db, request)
    user_response = UserResponse.model_validate(user)
    return UserSetIsActiveResponse(user=user_response, reassigned_prs=reassigned_count)


@router.get(
    "/users/getReview",
    response_model=UserReviewResponse,
    responses={
        200: {"description": "Список PR'ов пользователя"},
        404: {"model": ErrorResponse, "description": "Пользователь не найден"},
    },
)
async def get_user_reviews(
    user_id: str = Query(..., description="Идентификатор пользователя"),
    db: Session = Depends(get_db),
):
    """Получить PR'ы, где пользователь назначен ревьювером"""
    prs = UserService.get_user_reviews(db, user_id)
    pr_shorts = [PullRequestShort.model_validate(pr) for pr in prs]
    return UserReviewResponse(user_id=user_id, pull_requests=pr_shorts)


@router.post(
    "/users/bulkDeactivate",
    response_model=BulkDeactivateResponse,
    responses={
        200: {"description": "Пользователи деактивированы"},
        404: {
            "model": ErrorResponse,
            "description": "Пользователи не найдены или не принадлежат команде",
        },
    },
)
async def bulk_deactivate(request: BulkDeactivateRequest, db: Session = Depends(get_db)):
    """
    Массовая деактивация пользователей команды.
    (автоматически переназначаются ревьюверы в открытых PR)
    """
    users, reassigned_count = UserService.bulk_deactivate(db, request)
    user_responses = [UserResponse.model_validate(user) for user in users]
    return BulkDeactivateResponse(deactivated_users=user_responses, reassigned_prs=reassigned_count)
