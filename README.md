# Polymind IA - Backend

Backend de la plataforma multiagente Polymind IA, construido con FastAPI, SQLAlchemy y gRPC.

## Despliegue

Desplegado en Vercel:

| | URL | Repositorio |
|---|---|---|
| Aplicación (frontend) | https://polymind-front.vercel.app | [Juanp-lucero/polymind-front](https://github.com/Juanp-lucero/polymind-front) |
| API (backend) | https://polymind-back.vercel.app | [Juanp-lucero/polymind-back](https://github.com/Juanp-lucero/polymind-back) |
| Estado de la API | https://polymind-back.vercel.app/health | |
| Documentación de la API | https://polymind-back.vercel.app/docs | |

## Requisitos

- Python 3.10 o superior
- PostgreSQL
- Dependencias de `requirements.txt`
- Una API key de Groq para habilitar la generación de informes con IA (opcional)

## Instalación

```bash
python -m venv venv
# Windows:
venv\\Scripts\\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

Copia `.env.example` como `.env` y completa las variables necesarias para tu entorno. Conserva las variables existentes de base de datos y autenticación. No subas nunca el archivo `.env` ni compartas claves privadas.

Variables nuevas para Groq:

- `GROQ_API_KEY`: clave privada de Groq.
- `GROQ_MODEL`: modelo a utilizar. Por defecto: `llama-3.3-70b-versatile`.

Puedes obtener la clave desde https://console.groq.com/keys.

## Ejecutar

Inicia el servidor FastAPI:

```bash
uvicorn app.main:app --reload
```

En otra terminal, inicia el servidor gRPC multiagente:

```bash
python -m app.grpc_service.grpc_server
```

La API REST utiliza el servicio gRPC para ejecutar el análisis de decisiones.

## Arquitectura multiagente con IA

```
Frontend ──REST──▶ FastAPI ──gRPC──▶ Orquestador
                                      ├─ Financial Agent    ┐
                                      ├─ Technology Agent   │ en paralelo,
                                      ├─ Human Impact Agent │ cada uno con IA
                                      └─ Risk Agent         ┘ y respaldo por reglas
                                                 │
                                                 ▼
                                        Analyst Agent ──▶ informe final
```

1. **Agentes especialistas** (`app/agents/*_agent.py`). Cada uno evalúa todas las alternativas desde su perspectiva (costos, tecnología, personas y riesgos). Le pide a Groq un JSON con una puntuación de 1 a 10 y una justificación por alternativa, y valida la respuesta (`BaseAgent.validate_ai_result`):
   - todas las alternativas deben estar evaluadas;
   - las puntuaciones se limitan a 1–10;
   - las justificaciones no pueden estar vacías;
   - se ignoran las alternativas inventadas.
   Si la respuesta no es válida o Groq no está disponible, el agente usa sus reglas (`rule_based_analyze`).
2. **Orquestador** (`app/agents/orchestrator.py`). Ejecuta los cuatro agentes en paralelo. Si uno falla, recupera su evaluación por reglas para no perder el análisis.
3. **Agente analista** (`app/agents/analyst_agent.py`). Pondera los resultados (financiero 30 %, tecnológico 30 %, humano 20 %, riesgos 20 %) y ordena las alternativas. Además:
   - detecta los **desacuerdos** entre agentes (diferencia de 4 puntos o más);
   - avisa cuando la decisión tiene **información insuficiente**.
   Groq redacta el informe ejecutivo con esos datos. Si no está disponible, se usa un informe local.

Cada agente indica en sus observaciones si su evaluación se hizo con IA o con reglas.

### Variables de IA

| Variable | Descripción |
|---|---|
| `GROQ_API_KEY` | Llave de Groq. Sin ella todo funciona con reglas. |
| `GROQ_MODEL` | Modelo (por defecto `llama-3.3-70b-versatile`). |

## Pruebas

```bash
pip install -r requirements.txt pytest httpx
pytest
```

Las pruebas usan una base SQLite temporal y nunca llaman a Groq. Cubren:
- autenticación y renovación de tokens;
- CRUD de decisiones y aislamiento entre usuarios;
- el flujo completo de análisis por gRPC en proceso;
- la validación de las respuestas de la IA, el orquestador, el analista y las estadísticas.

## Documentación de API

Con FastAPI en ejecución, visita:

- Swagger UI: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health
