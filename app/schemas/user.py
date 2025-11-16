from typing import List

from pydantic import BaseModel, ConfigDict

from app.schemas.pull_request import PullRequestShort


class UserBase(BaseModel):
    """Базовая схема пользователя"""

    user_id: str
    username: str
    team_name: str
    is_active: bool


class UserResponse(UserBase):
    """Схема ответа"""

    model_config = ConfigDict(from_attributes=True)


class SetIsActiveRequest(BaseModel):
    """Схема запроса установки активности пользователя"""

    user_id: str
    is_active: bool


class UserReviewResponse(BaseModel):
    """Схема ответа на запрос списка PR пользователя"""

    model_config = ConfigDict(from_attributes=True)

    user_id: str
    pull_requests: List[PullRequestShort]


class UserSetIsActiveResponse(BaseModel):
    """Схема ответа на запрос установки активности пользователя"""

    user: UserResponse
    reassigned_prs: int = 0


class BulkDeactivateRequest(BaseModel):
    """Схема запроса массовой деактивации пользователей"""

    team_name: str
    user_ids: List[str]


class BulkDeactivateResponse(BaseModel):
    """Схема ответа на запрос массовой деактивации пользователей"""

    deactivated_users: List[UserResponse]
    reassigned_prs: int
