
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AnalysisResponse(BaseModel):
    id: int
    decision_id: int
    analysis: str
    recommendations: list[str]
    status: str
    created_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class AnalysisDetailResponse(BaseModel):
    id: int
    analysis_id: int
    agent_results: list[dict]
    alternative_comparison: list[dict]
    weights: dict
    created_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
