from fastapi import FastAPI

from app.core.database import Base, engine
from app.models.user import User
from app.models.decision import Decision
from app.routers.auth import router as auth_router
from app.routers.decisions import router as decisions_router
from app.models.analysis import Analysis
from app.models.analysis_detail import AnalysisDetail

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Polymind IA",
    description="Plataforma multiagente para la toma de decisiones complejas",
    version="1.0.0"
)


app.include_router(auth_router)
app.include_router(decisions_router)


@app.get("/")
def root():
    return {
        "message": "Polymind IA Backend funcionando",
        "status": "online"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
