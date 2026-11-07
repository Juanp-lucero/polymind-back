from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DecisionCreate(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    description: str = Field(min_length=10)
    context: Optional[str] = None
    alternatives: list[str] = Field(default_factory=list)


class DecisionUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=150)
    description: Optional[str] = Field(default=None, min_length=10)
    context: Optional[str] = None
    alternatives: Optional[list[str]] = None
    status: Optional[str] = Field(
        default=None,
        pattern="^(pending|in_progress|completed|cancelled)$"
    )


class DecisionResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    context: Optional[str]
    alternatives: list[str]
    status: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
