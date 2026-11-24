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

## Integración Groq

Groq genera la síntesis narrativa del informe a partir de las evaluaciones de los agentes financiero, tecnológico, de impacto humano y de riesgos.

Las puntuaciones, ponderaciones y comparación de alternativas continúan calculándose en el backend. La IA interpreta esos resultados y redacta el informe; no inventa ni modifica las puntuaciones.

Si `GROQ_API_KEY` no está configurada o Groq no está disponible, Polymind utiliza el informe local de respaldo y puede continuar el análisis. Esto permite desarrollar y probar el resto del sistema sin depender de la API externa.

## Documentación de API

Con FastAPI en ejecución, visita:

- Swagger UI: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health
