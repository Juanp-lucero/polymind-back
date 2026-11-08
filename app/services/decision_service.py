
from sqlalchemy.orm import Session

from app.models.decision import Decision
from app.schemas.decision import DecisionCreate, DecisionUpdate


def create_decision(
    db: Session,
    decision_data: DecisionCreate,
    user_id: int
):
    new_decision = Decision(
        user_id=user_id,
        title=decision_data.title,
        description=decision_data.description,
        context=decision_data.context,
        alternatives=decision_data.alternatives,
        status="pending"
    )

    db.add(new_decision)
    db.commit()
    db.refresh(new_decision)

    return new_decision


def get_user_decisions(db: Session, user_id: int):
    return (
        db.query(Decision)
        .filter(Decision.user_id == user_id)
        .order_by(Decision.created_at.desc())
        .all()
    )


def get_decision_by_id(
    db: Session,
    decision_id: int,
    user_id: int
):
    return (
        db.query(Decision)
        .filter(
            Decision.id == decision_id,
            Decision.user_id == user_id
        )
        .first()
    )


def update_decision(
    db: Session,
    decision: Decision,
    decision_data: DecisionUpdate
):
    update_data = decision_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(decision, field, value)

    db.commit()
    db.refresh(decision)

    return decision


def delete_decision(db: Session, decision: Decision):
    db.delete(decision)
    db.commit()

    return True
