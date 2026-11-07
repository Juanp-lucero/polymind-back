
from app.agents.base_agent import BaseAgent


class HumanImpactAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="Human Impact Agent",
            description="Analiza las consecuencias humanas y sociales de las decisiones."
        )

    def analyze(self, decision: dict) -> dict:

        title = decision.get("title", "")
        description = decision.get("description", "")
        context = decision.get("context", "")
        alternatives = decision.get("alternatives", [])

        if not alternatives:
            return self.create_response(
                analysis="No existen alternativas para evaluar el impacto humano.",
                recommendations=[
                    "Agregar alternativas antes de realizar el análisis."
                ],
                observations=["No se recibieron alternativas."]
            )

        recommendations = [
            "Identificar cómo afectará cada alternativa a los empleados.",
            "Evaluar los beneficios para los clientes y usuarios.",
            "Considerar las necesidades de capacitación del personal.",
            "Analizar posibles cambios en las condiciones laborales.",
            "Garantizar que la solución sea accesible y fácil de utilizar."
        ]

        observations = [
            f"Cantidad de alternativas evaluadas: {len(alternatives)}.",
            "No se proporcionaron encuestas ni datos específicos de los usuarios."
        ]

        analysis = (
            f"El análisis de impacto humano de la decisión '{title}' "
            f"busca identificar las consecuencias que puede generar "
            f"cada alternativa sobre las personas involucradas. "
            f"Descripción: {description}. "
            f"Contexto: {context}. "
            f"Se deben considerar la experiencia de los usuarios, "
            f"las condiciones de los empleados y las necesidades de adaptación."
        )

        return self.create_response(
            analysis=analysis,
            recommendations=recommendations,
            observations=observations
        )
