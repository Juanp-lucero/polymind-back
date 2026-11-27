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

## Cambios recientes

Durante el despliegue en producción se hicieron los siguientes cambios pertinentes, por la vigencia de los servicios externos (APIs) y la configuración del servidor:

- **Inicio de sesión y API caídos:** en producción, SQLAlchemy 2.1 necesita el driver `psycopg`, que no estaba instalado. Todas las peticiones a la base de datos, incluido el login, respondían con error 500. Se agregó la dependencia en `requirements.txt`.
- **IA y API keys:** Groq retiró el modelo `llama-3.3-70b-versatile` en agosto de 2026 y los agentes dejaron de responder con IA. Se cambió a `openai/gpt-oss-120b`, con un modelo de respaldo automático. La llave se configuró como variable de entorno en Vercel y no queda en el código.
- **Respaldo sin IA:** cada agente tiene reglas heurísticas, así que el análisis funciona aunque Groq falle.

## Cuenta de prueba

Para revisar Polymind IA sin registrarse:

| Aplicación | Correo | Contraseña |
|---|---|---|
| https://polymind-front.vercel.app | `profesor.demo@example.com` | `ProfeDemo2026*` |

Es una cuenta de demostración creada solo para la evaluación; no contiene datos personales.

## Cómo probarlo

1. Entra a https://polymind-front.vercel.app e inicia sesión con la [cuenta de prueba](#cuenta-de-prueba) (o crea una cuenta en **Crear cuenta**).
2. **Decisiones → Nueva decisión**. Datos de ejemplo:
   - **Título de la decisión:** `Elegir plataforma para el sistema de inventario`
   - **Descripción del reto:** `La empresa necesita reemplazar su hoja de cálculo de inventario. Hay 15 usuarios, presupuesto anual de 20 millones de pesos y el equipo de TI tiene 2 personas con experiencia en Python.`
   - **Contexto adicional:** `El sistema debe estar en producción en 4 meses y conectarse con la facturación electrónica.`
   - **Alternativas a evaluar** (una por casilla; usa **＋ Añadir alternativa** para la tercera): `Desarrollo propio con Django`, `SaaS de inventario (Odoo)`, `Mejorar la hoja de cálculo actual`

   Pulsa **Guardar decisión**.
3. En el detalle, pulsa **Ejecutar análisis**. Se ven los pasos del análisis mientras los agentes trabajan.
4. Revisa el resultado:
   - la puntuación ponderada de cada alternativa y la recomendada;
   - la evaluación de cada agente con su justificación y la etiqueta **IA** o **Reglas**;
   - los **desacuerdos** entre agentes;
   - el aviso de **información insuficiente** cuando la descripción es muy corta;
   - el **informe ejecutivo**.
5. Usa **Editar** para cambiar la decisión y vuelve a analizarla. **Eliminar** pide confirmación.
6. En **Resumen** está el total de decisiones y el estado del sistema (API y IA).

## Cómo funciona

```
Angular (Vercel) ──REST + JWT──▶ FastAPI (Vercel) ──gRPC──▶ Orquestador
                                      │                     ├─ Agente financiero   (30 %)
                                      ▼                     ├─ Agente tecnológico  (30 %)
                               PostgreSQL (Neon)            ├─ Agente de impacto humano (20 %)
                                                            └─ Agente de riesgos   (20 %)
                                                                       │
                                                                       ▼
                                                             Agente analista ──▶ informe
```

1. **Agentes especialistas:** los cuatro evalúan todas las alternativas en paralelo, cada uno desde su perspectiva. Cada uno pide a Groq (`openai/gpt-oss-120b`) un JSON con puntuación de 1 a 10 y justificación por alternativa. Antes de usarlo, el backend comprueba que:
   - estén todas las alternativas;
   - las puntuaciones estén entre 1 y 10;
   - no haya justificaciones vacías ni alternativas inventadas.
   Si algo falla, ese agente usa sus reglas heurísticas.
2. **Agente analista:** pondera las puntuaciones, ordena las alternativas, detecta desacuerdos (4 puntos o más de diferencia) y vacíos de información. Groq redacta el informe ejecutivo; sin IA se genera un informe local.
3. **Sesión:** el access token se renueva solo con el refresh token cuando vence.
4. **Sin IA no se rompe nada:** cada paso tiene respaldo por reglas. Si el modelo configurado deja de existir, el backend prueba otro automáticamente.

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
- `GROQ_MODEL`: modelo a utilizar. Por defecto: `openai/gpt-oss-120b`.

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
| `GROQ_MODEL` | Modelo (por defecto `openai/gpt-oss-120b`). |

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
