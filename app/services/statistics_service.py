from collections import Counter
from typing import Counter as CounterType

from sqlalchemy.orm import Session

from app.models import PullRequest, User
from app.models.pull_request import PRStatus
from app.schemas.statistics import PRStats, StatisticsResponse, UserReviewStats


class StatisticsService:
    @staticmethod
    def get_statistics(db: Session) -> StatisticsResponse:
        """Получить статистику по PR и назначениям ревьюверов"""
        all_prs = db.query(PullRequest).all()

        total_prs = len(all_prs)
        open_prs = sum(1 for pr in all_prs if pr.status == PRStatus.OPEN)
        merged_prs = sum(1 for pr in all_prs if pr.status == PRStatus.MERGED)

        pr_stats = PRStats(total_prs=total_prs, open_prs=open_prs, merged_prs=merged_prs)

        reviewer_counts: CounterType[str] = Counter()
        for pr in all_prs:
            for reviewer_id in pr.assigned_reviewers:
                reviewer_counts[reviewer_id] += 1

        user_review_stats = []
        for user_id, count in reviewer_counts.items():
            user = db.query(User).filter(User.user_id == user_id).first()
            if user:
                user_review_stats.append(
                    UserReviewStats(
                        user_id=user_id, username=user.username, assignments_count=count
                    )
                )

        user_review_stats.sort(key=lambda x: x.assignments_count, reverse=True)

        return StatisticsResponse(pr_stats=pr_stats, user_review_stats=user_review_stats)
