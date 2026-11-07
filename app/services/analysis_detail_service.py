
from sqlalchemy.orm import Session

from app.models.analysis_detail import AnalysisDetail


def create_analysis_detail(
    db: Session,
    analysis_id: int,
    agent_results: list[dict],
    alternative_comparison: list[dict],
    weights: dict
):
    new_detail = AnalysisDetail(
        analysis_id=analysis_id,
        agent_results=agent_results,
        alternative_comparison=alternative_comparison,
        weights=weights
    )

    db.add(new_detail)
    db.commit()
    db.refresh(new_detail)

    return new_detail


def get_analysis_detail(
    db: Session,
    analysis_id: int
):
    return (
        db.query(AnalysisDetail)
        .filter(AnalysisDetail.analysis_id == analysis_id)
        .first()
    )


def update_analysis_detail(
    db: Session,
    detail: AnalysisDetail,
    agent_results: list[dict],
    alternative_comparison: list[dict],
    weights: dict
):
    detail.agent_results = agent_results
    detail.alternative_comparison = alternative_comparison
    detail.weights = weights

    db.commit()
    db.refresh(detail)

    return detail


def delete_analysis_detail(
    db: Session,
    detail: AnalysisDetail
):
    db.delete(detail)
    db.commit()

    return True
