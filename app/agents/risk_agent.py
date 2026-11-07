
from app.agents.base_agent import BaseAgent


class RiskAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="Risk Agent",
            description="Identifica y evalúa los riesgos asociados a las decisiones."
        )

    def analyze(self, decision: dict) -> dict:

        title = decision.get("title", "")
        description = decision.get("description", "")
        context = decision.get("context", "")
        alternatives = decision.get("alternatives", [])

        if not alternatives:
            return self.create_response(
                analysis="No existen alternativas para evaluar los riesgos.",
                recommendations=[
                    "Agregar alternativas antes de realizar el análisis."
                ],
                observations=["No se recibieron alternativas."]
            )

        recommendations = [
            "Identificar posibles fallos durante la implementación.",
            "Evaluar los riesgos financieros y operativos.",
            "Establecer medidas para prevenir incidentes.",
            "Crear un plan de contingencia para cada alternativa.",
            "Realizar seguimiento periódico de los riesgos identificados."
        ]

        observations = [
            f"Cantidad de alternativas evaluadas: {len(alternatives)}.",
            "No se proporcionaron datos históricos para calcular probabilidades de riesgo."
        ]

        analysis = (
            f"El análisis de riesgos de la decisión '{title}' "
            f"busca identificar situaciones que puedan afectar "
            f"el cumplimiento de los objetivos. "
            f"Descripción: {description}. "
            f"Contexto: {context}. "
            f"Se deben evaluar los posibles problemas técnicos, "
            f"financieros, operativos y organizacionales de cada alternativa."
        )

        return self.create_response(
            analysis=analysis,
            recommendations=recommendations,
            observations=observations
        )
