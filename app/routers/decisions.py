import grpc

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.decision import (
    DecisionCreate,
    DecisionUpdate,
    DecisionResponse
)
from app.services import decision_service
from app.grpc_service.grpc_client import analyze_decision


router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"]
)


@router.post("/", response_model=DecisionResponse, status_code=201)
def create_new_decision(
    decision_data: DecisionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return decision_service.create_decision(
        db, decision_data, current_user.id
    )


@router.get("/", response_model=list[DecisionResponse])
def list_decisions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return decision_service.get_user_decisions(
        db, current_user.id
    )


@router.get("/{decision_id}", response_model=DecisionResponse)
def get_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = decision_service.get_decision_by_id(
        db, decision_id, current_user.id
    )

    if decision is None:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    return decision


@router.post("/{decision_id}/analyze")
def analyze_existing_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = decision_service.get_decision_by_id(
        db, decision_id, current_user.id
    )

    if decision is None:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    if not decision.alternatives:
        raise HTTPException(
            status_code=422,
            detail="At least one alternative is required"
        )

    try:
        result = analyze_decision(
            decision_id=decision.id,
            title=decision.title,
            description=decision.description,
            context=decision.context or "",
            alternatives=decision.alternatives
        )

        return {
            "decision_id": result.decision_id,
            "status": result.status,
            "analysis": result.analysis,
            "recommendations": list(result.recommendations)
        }

    except grpc.RpcError as error:

        if error.code() == grpc.StatusCode.INVALID_ARGUMENT:
            raise HTTPException(
                status_code=422,
                detail=error.details()
            )

        raise HTTPException(
            status_code=503,
            detail="The gRPC analysis service is unavailable"
        )


@router.put("/{decision_id}", response_model=DecisionResponse)
def update_existing_decision(
    decision_id: int,
    decision_data: DecisionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = decision_service.get_decision_by_id(
        db, decision_id, current_user.id
    )

    if decision is None:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    return decision_service.update_decision(
        db, decision, decision_data
    )


@router.delete("/{decision_id}", status_code=204)
def delete_existing_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = decision_service.get_decision_by_id(
        db, decision_id, current_user.id
    )

    if decision is None:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    decision_service.delete_decision(db, decision)

    return None