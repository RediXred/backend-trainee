from typing import List

from pydantic import BaseModel, ConfigDict


class TeamMember(BaseModel):
    """Схема участника команды"""

    model_config = ConfigDict(from_attributes=True)

    user_id: str
    username: str
    is_active: bool


class TeamBase(BaseModel):
    """Схема команды"""

    team_name: str
    members: List[TeamMember]


class TeamCreate(TeamBase):
    """Схема создания команды"""

    pass


class TeamResponse(TeamBase):
    """Схема ответа"""

    model_config = ConfigDict(from_attributes=True)


class TeamCreateResponse(BaseModel):
    """Схема ответа создания команды"""

    team: TeamResponse
