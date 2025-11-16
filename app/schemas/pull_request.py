from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.pull_request import PRStatus


class PullRequestCreate(BaseModel):
    """Схема создания PR"""

    pull_request_id: str
    pull_request_name: str
    author_id: str


class PullRequestCreateResponseItem(BaseModel):
    """Схема PR для ответа create"""

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    pull_request_id: str
    pull_request_name: str
    author_id: str
    status: PRStatus
    assigned_reviewers: List[str] = Field(default_factory=list)


class PullRequestMergeResponseItem(BaseModel):
    """Схема PR для ответа merge"""

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    pull_request_id: str
    pull_request_name: str
    author_id: str
    status: PRStatus
    assigned_reviewers: List[str] = Field(default_factory=list)
    merged_at: Optional[datetime] = Field(None, alias="mergedAt")


class PullRequestReassignResponseItem(BaseModel):
    """Схема PR для ответа reassign"""

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    pull_request_id: str
    pull_request_name: str
    author_id: str
    status: PRStatus
    assigned_reviewers: List[str] = Field(default_factory=list)


class PullRequestShort(BaseModel):
    """Схема краткого PR"""

    model_config = ConfigDict(from_attributes=True)

    pull_request_id: str
    pull_request_name: str
    author_id: str
    status: PRStatus


class MergePRRequest(BaseModel):
    """Схема запроса merge PR"""

    pull_request_id: str


class ReassignPRRequest(BaseModel):
    """Схема запроса переназначения PR"""

    pull_request_id: str
    old_user_id: str


class ReassignPRResponse(BaseModel):
    """Схема ответа переназначения PR"""

    pr: PullRequestReassignResponseItem
    replaced_by: str


class PullRequestCreateResponse(BaseModel):
    """Схема ответа создания PR"""

    pr: PullRequestCreateResponseItem


class PullRequestMergeResponse(BaseModel):
    """Схема ответа merge PR"""

    pr: PullRequestMergeResponseItem
