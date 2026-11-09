from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.decision import Decision
from app.models.analysis import Analysis
from app.models.analysis_detail import AnalysisDetail


def get_user_statistics(db: Session, user_id: int):
    # Total de decisiones del usuario
    total_decisions = (
        db.query(func.count(Decision.id))
        .filter(Decision.user_id == user_id)
        .scalar()
    ) or 0

    # Total de análisis asociados a sus decisiones
    total_analyses = (
        db.query(func.count(Analysis.id))
        .join(Decision, Analysis.decision_id == Decision.id)
        .filter(Decision.user_id == user_id)
        .scalar()
    ) or 0

    # Análisis agrupados por estado
    status_rows = (
        db.query(Analysis.status, func.count(Analysis.id))
        .join(Decision, Analysis.decision_id == Decision.id)
        .filter(Decision.user_id == user_id)
        .group_by(Analysis.status)
        .all()
    )

    analyses_by_status = {
        status: count for status, count in status_rows
    }

    # Detalles de los análisis del usuario
    detail_rows = (
        db.query(AnalysisDetail)
        .join(Analysis, AnalysisDetail.analysis_id == Analysis.id)
        .join(Decision, Analysis.decision_id == Decision.id)
        .filter(Decision.user_id == user_id)
        .all()
    )

    total_scores = []
    recommended_alternatives = {}

    for detail in detail_rows:
        comparisons = detail.alternative_comparison or []

        valid_comparisons = [
            item for item in comparisons
            if isinstance(item, dict)
            and isinstance(item.get("weighted_score"), (int, float))
        ]

        for item in valid_comparisons:
            total_scores.append(float(item["weighted_score"]))

        # Identificar la alternativa con mayor puntuación
        if valid_comparisons:
            winner = max(
                valid_comparisons,
                key=lambda item: item["weighted_score"]
            )

            alternative_name = winner.get("alternative")

            if alternative_name:
                recommended_alternatives[alternative_name] = (
                    recommended_alternatives.get(alternative_name, 0) + 1
                )

    average_score = (
        sum(total_scores) / len(total_scores)
        if total_scores else 0
    )

    top_recommendations = [
        {
            "alternative": alternative,
            "times_recommended": count
        }
        for alternative, count in sorted(
            recommended_alternatives.items(),
            key=lambda item: item[1],
            reverse=True
        )
    ]

    return {
        "total_decisions": total_decisions,
        "total_analyses": total_analyses,
        "analyses_by_status": analyses_by_status,
        "average_score": round(average_score, 2),
        "top_recommendations": top_recommendations
    }