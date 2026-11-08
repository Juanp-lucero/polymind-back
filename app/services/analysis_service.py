
from sqlalchemy.orm import Session

from app.models.analysis import Analysis


def create_analysis(
    db: Session,
    decision_id: int,
    analysis_text: str,
    recommendations: list[str],
    status: str = "completed",
    commit: bool = True
):
    new_analysis = Analysis(
        decision_id=decision_id,
        analysis=analysis_text,
        recommendations=recommendations,
        status=status
    )

    db.add(new_analysis)
    db.flush()
    db.refresh(new_analysis)

    if commit:
        db.commit()
        db.refresh(new_analysis)

    return new_analysis


def get_decision_analyses(
    db: Session,
    decision_id: int
):
    return (
        db.query(Analysis)
        .filter(Analysis.decision_id == decision_id)
        .order_by(Analysis.created_at.desc())
        .all()
    )


def get_analysis_by_id(
    db: Session,
    analysis_id: int,
    decision_id: int
):
    return (
        db.query(Analysis)
        .filter(
            Analysis.id == analysis_id,
            Analysis.decision_id == decision_id
        )
        .first()
    )
