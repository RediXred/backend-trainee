import json
import random
from typing import List, Tuple

from fastapi import HTTPException
from sqlalchemy import or_, text
from sqlalchemy.orm import Session

from app.models import PullRequest, User
from app.models.pull_request import PRStatus
from app.schemas.error import ErrorDetail, ErrorResponse
from app.schemas.user import BulkDeactivateRequest, SetIsActiveRequest


class UserService:
    @staticmethod
    def _reassign_reviewers(db: Session, user_ids: List[str]) -> int:
        """
        Метод переназначения ревьюверов в открытых PR
        для одного или нескольких пользователей.
        Возвращает количество PR, где были переназначены ревьюверы
        """
        if not user_ids:
            return 0

        conditions = []
        for user_id in user_ids:
            user_id_json = json.dumps([user_id])
            conditions.append(text(f"assigned_reviewers::jsonb @> '{user_id_json}'::jsonb"))

        open_prs = (
            db.query(PullRequest)
            .filter(
                PullRequest.status == PRStatus.OPEN,
                or_(*conditions) if conditions else text("1=0"),
            )
            .all()
        )
        if not open_prs:
            return 0

        users_dict = {
            user.user_id: user for user in db.query(User).filter(User.user_id.in_(user_ids)).all()
        }

        reassigned_count = 0
        for pr in open_prs:
            deactivating_reviewers = [
                user_id
                for user_id in user_ids
                if user_id in pr.assigned_reviewers and user_id in users_dict
            ]
            if not deactivating_reviewers:
                continue

            for user_id in deactivating_reviewers:
                user = users_dict[user_id]
                available_reviewers = (
                    db.query(User)
                    .filter(
                        User.team_name == user.team_name,
                        User.user_id != user_id,
                        User.user_id.notin_(pr.assigned_reviewers),
                        User.user_id != pr.author_id,
                        User.user_id.notin_(user_ids),
                        User.is_active == True,
                    )
                    .all()
                )

                if available_reviewers:
                    new_reviewer = random.choice(available_reviewers)
                    reviewers = pr.assigned_reviewers.copy()
                    reviewers.remove(user_id)
                    reviewers.append(new_reviewer.user_id)
                    pr.assigned_reviewers = reviewers
                    reassigned_count += 1
                else:
                    reviewers = pr.assigned_reviewers.copy()
                    if user_id in reviewers:
                        reviewers.remove(user_id)
                        pr.assigned_reviewers = reviewers
                        reassigned_count += 1

        return reassigned_count

    @staticmethod
    def set_is_active(db: Session, request: SetIsActiveRequest) -> Tuple[User, int]:
        """
        Установить флаг активности пользователя;
        при деактивации переназначаются ревьюверы в открытых PR;
        возвращает кортеж (пользователь, количество переназначенных PR)
        """
        user = db.query(User).filter(User.user_id == request.user_id).first()
        if not user:
            error_response = ErrorResponse(
                error=ErrorDetail(code="NOT_FOUND", message="resource not found")
            )
            raise HTTPException(status_code=404, detail=error_response.model_dump())

        reassigned_count = 0
        if not request.is_active and user.is_active:
            reassigned_count = UserService._reassign_reviewers(db, [request.user_id])

        user.is_active = request.is_active
        db.commit()
        db.refresh(user)
        return user, reassigned_count

    @staticmethod
    def get_user_reviews(db: Session, user_id: str) -> list[PullRequest]:
        """Получить PR'ы, где пользователь назначен ревьювером"""

        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            error_response = ErrorResponse(
                error=ErrorDetail(code="NOT_FOUND", message="resource not found")
            )
            raise HTTPException(status_code=404, detail=error_response.model_dump())

        user_id_json = json.dumps([user_id])
        prs = (
            db.query(PullRequest)
            .filter(text(f"assigned_reviewers::jsonb @> '{user_id_json}'::jsonb"))
            .all()
        )

        return prs

    @staticmethod
    def bulk_deactivate(db: Session, request: BulkDeactivateRequest) -> Tuple[List[User], int]:
        """
        Массовая деактивация пользователей команды;
        переназначаются ревьюверы в открытых PR для всех деактивируемых пользователей;
        возвращает кортеж (список деактивированных пользователей, количество переназначенных PR)
        """
        users = (
            db.query(User)
            .filter(User.team_name == request.team_name, User.user_id.in_(request.user_ids))
            .all()
        )

        if len(users) != len(request.user_ids):
            found_user_ids = {user.user_id for user in users}
            missing_user_ids = set(request.user_ids) - found_user_ids
            error_response = ErrorResponse(
                error=ErrorDetail(
                    code="NOT_FOUND",
                    message=f"Users not found or not in team: {', '.join(missing_user_ids)}",
                )
            )
            raise HTTPException(status_code=404, detail=error_response.model_dump())

        active_user_ids = [user.user_id for user in users if user.is_active]

        total_reassigned_count = 0

        if active_user_ids:
            total_reassigned_count = UserService._reassign_reviewers(db, active_user_ids)

        for user in users:
            user.is_active = False

        db.commit()
        for user in users:
            db.refresh(user)

        return users, total_reassigned_count
