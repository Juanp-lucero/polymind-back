
import grpc

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User

from app.schemas.decision import (
    DecisionCreate,
    DecisionUpdate,
    DecisionResponse
)

from app.schemas.analysis import AnalysisResponse

from app.services import decision_service
from app.services import analysis_service

from app.grpc_service.grpc_client import analyze_decision


router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"]
)


# ==========================================
# CREAR DECISION
# ==========================================

@router.post("/", response_model=DecisionResponse, status_code=201)
def create_new_decision(
    decision_data: DecisionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return decision_service.create_decision(
        db,
        decision_data,
        current_user.id
    )


# ==========================================
# LISTAR DECISIONES
# ==========================================

@router.get("/", response_model=list[DecisionResponse])
def list_decisions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return decision_service.get_user_decisions(
        db,
        current_user.id
    )


# ==========================================
# OBTENER UNA DECISION
# ==========================================

@router.get("/{decision_id}", response_model=DecisionResponse)
def get_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = decision_service.get_decision_by_id(
        db,
        decision_id,
        current_user.id
    )

    if decision is None:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    return decision


# ==========================================
# ANALIZAR DECISION MEDIANTE gRPC
# Y GUARDAR RESULTADO EN POSTGRESQL
# ==========================================

@router.post(
    "/{decision_id}/analyze",
    response_model=AnalysisResponse
)
def analyze_existing_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = decision_service.get_decision_by_id(
        db,
        decision_id,
        current_user.id
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

    except grpc.RpcError:
        raise HTTPException(
            status_code=503,
            detail="The gRPC analysis service is unavailable"
        )

    try:
        saved_analysis = analysis_service.create_analysis(
            db=db,
            decision_id=decision.id,
            analysis_text=result.analysis,
            recommendations=list(result.recommendations),
            status="completed"
        )

        return saved_analysis

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not save the analysis"
        )


# ==========================================
# CONSULTAR HISTORIAL DE ANALISIS
# ==========================================

@router.get(
    "/{decision_id}/analyses",
    response_model=list[AnalysisResponse]
)
def get_decision_analysis_history(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = decision_service.get_decision_by_id(
        db,
        decision_id,
        current_user.id
    )

    if decision is None:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    return analysis_service.get_decision_analyses(
        db,
        decision.id
    )


# ==========================================
# ACTUALIZAR DECISION
# ==========================================

@router.put("/{decision_id}", response_model=DecisionResponse)
def update_existing_decision(
    decision_id: int,
    decision_data: DecisionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = decision_service.get_decision_by_id(
        db,
        decision_id,
        current_user.id
    )

    if decision is None:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    return decision_service.update_decision(
        db,
        decision,
        decision_data
    )


# ==========================================
# ELIMINAR DECISION
# ==========================================

@router.delete("/{decision_id}", status_code=204)
def delete_existing_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = decision_service.get_decision_by_id(
        db,
        decision_id,
        current_user.id
    )

    if decision is None:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    decision_service.delete_decision(db, decision)

    return None
