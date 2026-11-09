from pydantic import BaseModel


class RecommendationStat(BaseModel):
    alternative: str
    times_recommended: int


class StatisticsResponse(BaseModel):
    total_decisions: int
    total_analyses: int
    analyses_by_status: dict[str, int]
    average_score: float
    top_recommendations: list[RecommendationStat]