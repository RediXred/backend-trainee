import random
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import PullRequest, User
from app.models.pull_request import PRStatus
from app.schemas.error import ErrorDetail, ErrorResponse
from app.schemas.pull_request import PullRequestCreate, ReassignPRRequest


class PullRequestService:
    @staticmethod
    def create_pr(db: Session, pr_data: PullRequestCreate) -> PullRequest:
        """Создать PR и автоматически назначить до 2 ревьюверов из команды автора"""
        existing_pr = (
            db.query(PullRequest)
            .filter(PullRequest.pull_request_id == pr_data.pull_request_id)
            .first()
        )

        if existing_pr:
            error_response = ErrorResponse(
                error=ErrorDetail(code="PR_EXISTS", message="PR id already exists")
            )
            raise HTTPException(status_code=409, detail=error_response.model_dump())

        author = db.query(User).filter(User.user_id == pr_data.author_id).first()
        if not author:
            error_response = ErrorResponse(
                error=ErrorDetail(code="NOT_FOUND", message="resource not found")
            )
            raise HTTPException(status_code=404, detail=error_response.model_dump())

        team_members = (
            db.query(User)
            .filter(
                User.team_name == author.team_name,
                User.user_id != pr_data.author_id,
                User.is_active == True,
            )
            .all()
        )

        if team_members:
            reviewers = random.sample(team_members, min(2, len(team_members)))
            reviewer_ids = [reviewer.user_id for reviewer in reviewers]
        else:
            reviewer_ids = []
        pr = PullRequest(
            pull_request_id=pr_data.pull_request_id,
            pull_request_name=pr_data.pull_request_name,
            author_id=pr_data.author_id,
            status=PRStatus.OPEN,
            assigned_reviewers=reviewer_ids,
        )

        try:
            db.add(pr)
            db.commit()
            db.refresh(pr)
            return pr
        except IntegrityError:
            db.rollback()
            error_response = ErrorResponse(
                error=ErrorDetail(code="PR_EXISTS", message="PR id already exists")
            )
            raise HTTPException(status_code=409, detail=error_response.model_dump())

    @staticmethod
    def merge_pr(db: Session, pr_id: str) -> PullRequest:
        """Пометить PR как MERGED"""
        pr = db.query(PullRequest).filter(PullRequest.pull_request_id == pr_id).first()
        if not pr:
            error_response = ErrorResponse(
                error=ErrorDetail(code="NOT_FOUND", message="resource not found")
            )
            raise HTTPException(status_code=404, detail=error_response.model_dump())

        if pr.status == PRStatus.MERGED:
            return pr
        pr.status = PRStatus.MERGED
        pr.merged_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(pr)
        return pr

    @staticmethod
    def reassign_reviewer(db: Session, request: ReassignPRRequest) -> tuple[PullRequest, str]:
        """Переназначить конкретного ревьювера на другого из команды"""
        pr = (
            db.query(PullRequest)
            .filter(PullRequest.pull_request_id == request.pull_request_id)
            .first()
        )

        if not pr:
            error_response = ErrorResponse(
                error=ErrorDetail(code="NOT_FOUND", message="resource not found")
            )
            raise HTTPException(status_code=404, detail=error_response.model_dump())

        if pr.status == PRStatus.MERGED:
            error_response = ErrorResponse(
                error=ErrorDetail(code="PR_MERGED", message="cannot reassign on merged PR")
            )
            raise HTTPException(status_code=409, detail=error_response.model_dump())
        if request.old_user_id not in pr.assigned_reviewers:
            error_response = ErrorResponse(
                error=ErrorDetail(
                    code="NOT_ASSIGNED", message="reviewer is not assigned to this PR"
                )
            )
            raise HTTPException(status_code=409, detail=error_response.model_dump())

        old_reviewer = db.query(User).filter(User.user_id == request.old_user_id).first()
        if not old_reviewer:
            error_response = ErrorResponse(
                error=ErrorDetail(code="NOT_FOUND", message="resource not found")
            )
            raise HTTPException(status_code=404, detail=error_response.model_dump())

        available_reviewers = (
            db.query(User)
            .filter(
                User.team_name == old_reviewer.team_name,
                User.user_id != request.old_user_id,
                User.user_id.notin_(pr.assigned_reviewers),
                User.user_id != pr.author_id,
                User.is_active == True,
            )
            .all()
        )

        if not available_reviewers:
            error_response = ErrorResponse(
                error=ErrorDetail(
                    code="NO_CANDIDATE",
                    message="no active replacement candidate in team",
                )
            )
            raise HTTPException(status_code=409, detail=error_response.model_dump())

        new_reviewer = random.choice(available_reviewers)

        reviewers = pr.assigned_reviewers.copy()
        reviewers.remove(request.old_user_id)
        reviewers.append(new_reviewer.user_id)
        pr.assigned_reviewers = reviewers

        db.commit()
        db.refresh(pr)

        return pr, new_reviewer.user_id
