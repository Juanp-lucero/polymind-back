
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

from app.schemas.analysis import (
    AnalysisResponse,
    AnalysisDetailResponse
)

from app.services import (
    decision_service,
    analysis_service,
    analysis_detail_service
)

from app.grpc_service.grpc_client import analyze_decision


router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"]
)


# CREAR DECISION
@router.post("/", response_model=DecisionResponse)
def create_decision(
    data: DecisionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return decision_service.create_decision(
        db,
        data,
        current_user.id
    )


# LISTAR DECISIONES
@router.get("/", response_model=list[DecisionResponse])
def get_decisions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return decision_service.get_user_decisions(
        db,
        current_user.id
    )


# CONSULTAR UNA DECISION
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

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decisión no encontrada"
        )

    return decision


# ACTUALIZAR DECISION
@router.put("/{decision_id}", response_model=DecisionResponse)
def update_decision(
    decision_id: int,
    data: DecisionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = decision_service.get_decision_by_id(
        db,
        decision_id,
        current_user.id
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decisión no encontrada"
        )

    return decision_service.update_decision(
        db,
        decision,
        data
    )


# ELIMINAR DECISION
@router.delete("/{decision_id}")
def delete_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = decision_service.get_decision_by_id(
        db,
        decision_id,
        current_user.id
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decisión no encontrada"
        )

    decision_service.delete_decision(db, decision)

    return {
        "message": "Decisión eliminada correctamente"
    }


# EJECUTAR ANALISIS MULTIAGENTE
@router.post(
    "/{decision_id}/analyze",
    response_model=AnalysisResponse
)
def analyze_user_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = decision_service.get_decision_by_id(
        db,
        decision_id,
        current_user.id
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decisión no encontrada"
        )

    if not decision.alternatives:
        raise HTTPException(
            status_code=400,
            detail="La decisión debe tener al menos una alternativa"
        )

    try:
        result = analyze_decision(
            decision_id=decision.id,
            title=decision.title,
            description=decision.description,
            context=decision.context or "",
            alternatives=decision.alternatives
        )

        saved_analysis = analysis_service.create_analysis(
            db=db,
            decision_id=decision.id,
            analysis_text=result["analysis"],
            recommendations=result["recommendations"],
            status=result["status"]
        )

        analysis_detail_service.create_analysis_detail(
            db=db,
            analysis_id=saved_analysis.id,
            agent_results=result["agent_results"],
            alternative_comparison=result["alternative_comparison"],
            weights=result["weights"]
        )

        return saved_analysis

    except grpc.RpcError as error:
        db.rollback()

        raise HTTPException(
            status_code=503,
            detail=f"Error en el servicio gRPC: {error.details()}"
        )

    except Exception as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Error al guardar el análisis: {str(error)}"
        )


# CONSULTAR HISTORIAL DE ANALISIS
@router.get(
    "/{decision_id}/analyses",
    response_model=list[AnalysisResponse]
)
def get_analyses(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = decision_service.get_decision_by_id(
        db,
        decision_id,
        current_user.id
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decisión no encontrada"
        )

    return analysis_service.get_decision_analyses(
        db,
        decision_id
    )


# CONSULTAR DETALLES DE UN ANALISIS
@router.get(
    "/{decision_id}/analyses/{analysis_id}/details",
    response_model=AnalysisDetailResponse
)
def get_analysis_details(
    decision_id: int,
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = decision_service.get_decision_by_id(
        db,
        decision_id,
        current_user.id
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decisión no encontrada"
        )

    analysis = analysis_service.get_analysis_by_id(
        db,
        analysis_id,
        decision_id
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="Análisis no encontrado"
        )

    detail = analysis_detail_service.get_analysis_detail(
        db,
        analysis_id
    )

    if not detail:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron detalles del análisis"
        )

    return detail
