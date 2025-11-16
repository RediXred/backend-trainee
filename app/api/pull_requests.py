from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.base import get_db
from app.schemas.error import ErrorResponse
from app.schemas.pull_request import (
    MergePRRequest,
    PullRequestCreate,
    PullRequestCreateResponse,
    PullRequestCreateResponseItem,
    PullRequestMergeResponse,
    PullRequestMergeResponseItem,
    PullRequestReassignResponseItem,
    ReassignPRRequest,
    ReassignPRResponse,
)
from app.services.pull_request_service import PullRequestService

router = APIRouter()


@router.post(
    "/pullRequest/create",
    status_code=status.HTTP_201_CREATED,
    response_model=PullRequestCreateResponse,
    responses={
        201: {"description": "PR создан"},
        404: {"model": ErrorResponse, "description": "Автор/команда не найдены"},
        409: {"model": ErrorResponse, "description": "PR уже существует"},
    },
)
async def create_pr(pr_data: PullRequestCreate, db: Session = Depends(get_db)):
    """Создать PR и автоматически назначить ревьюверов из команды"""
    pr = PullRequestService.create_pr(db, pr_data)
    pr_response = PullRequestCreateResponseItem.model_validate(pr)
    return PullRequestCreateResponse(pr=pr_response)


@router.post(
    "/pullRequest/merge",
    response_model=PullRequestMergeResponse,
    responses={
        200: {"description": "PR в состоянии MERGED"},
        404: {"model": ErrorResponse, "description": "PR не найден"},
    },
)
async def merge_pr(request: MergePRRequest, db: Session = Depends(get_db)):
    """Пометить PR как MERGED"""
    pr = PullRequestService.merge_pr(db, request.pull_request_id)
    pr_response = PullRequestMergeResponseItem.model_validate(pr)
    return PullRequestMergeResponse(pr=pr_response)


@router.post(
    "/pullRequest/reassign",
    response_model=ReassignPRResponse,
    responses={
        200: {"description": "Переназначение выполнено"},
        404: {"model": ErrorResponse, "description": "PR или пользователь не найден"},
        409: {
            "model": ErrorResponse,
            "description": "Нарушение доменных правил переназначения",
        },
    },
)
async def reassign_reviewer(request: ReassignPRRequest, db: Session = Depends(get_db)):
    """Переназначить ревьювера на другого из его команды"""
    pr, new_reviewer_id = PullRequestService.reassign_reviewer(db, request)
    pr_response = PullRequestReassignResponseItem.model_validate(pr)
    return ReassignPRResponse(pr=pr_response, replaced_by=new_reviewer_id)
