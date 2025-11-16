from typing import List

from pydantic import BaseModel


class UserReviewStats(BaseModel):
    """Схема статистики назначений для одного пользователя"""

    user_id: str
    username: str
    assignments_count: int


class PRStats(BaseModel):
    """Схема общей статистики по PR"""

    total_prs: int
    open_prs: int
    merged_prs: int


class StatisticsResponse(BaseModel):
    """Схема ответа со статистикой"""

    pr_stats: PRStats
    user_review_stats: List[UserReviewStats]
