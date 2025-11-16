from typing import Literal

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Детали ошибки"""

    code: Literal[
        "TEAM_EXISTS",
        "PR_EXISTS",
        "PR_MERGED",
        "NOT_ASSIGNED",
        "NO_CANDIDATE",
        "NOT_FOUND",
    ]
    message: str


class ErrorResponse(BaseModel):
    """Схема ответа с ошибкой"""

    error: ErrorDetail
