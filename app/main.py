
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine

# Importar modelos para registrar las tablas
from app.models.user import User
from app.models.decision import Decision
from app.models.analysis import Analysis
from app.models.analysis_detail import AnalysisDetail

# Importar routers
from app.routers.auth import router as auth_router
from app.routers.decisions import router as decisions_router


# Crear las tablas de la base de datos
Base.metadata.create_all(bind=engine)


# Crear aplicación
app = FastAPI(
    title="Polymind IA",
    description="Plataforma multiagente para la toma de decisiones complejas",
    version="1.0.0"
)


# Configuración CORS
origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Registrar rutas
app.include_router(auth_router)
app.include_router(decisions_router)


# Ruta principal
@app.get("/")
def root():
    return {
        "message": "Polymind IA Backend funcionando",
        "status": "online"
    }


# Verificar estado del backend
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected"
    }
