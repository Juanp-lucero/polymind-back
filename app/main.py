from fastapi import FastAPI

from app.core.database import Base, engine
from app.models.user import User


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Polymind IA",
    description="Plataforma multiagente para la toma de decisiones complejas",
    version="1.0.0"
)


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