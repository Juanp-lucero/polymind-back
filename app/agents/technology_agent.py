
from app.agents.base_agent import BaseAgent


class TechnologyAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="Technology Agent",
            description="Analiza la viabilidad, infraestructura y recursos tecnológicos de las decisiones."
        )

    def analyze(self, decision: dict) -> dict:

        title = decision.get("title", "")
        description = decision.get("description", "")
        context = decision.get("context", "")
        alternatives = decision.get("alternatives", [])

        if not alternatives:
            return self.create_response(
                analysis=(
                    "No es posible realizar el análisis tecnológico "
                    "porque no existen alternativas."
                ),
                recommendations=[
                    "Agregar alternativas para evaluar su viabilidad tecnológica."
                ],
                observations=["No se recibieron alternativas."]
            )

        recommendations = [
            "Evaluar las tecnologías necesarias para cada alternativa.",
            "Verificar que la infraestructura disponible sea suficiente.",
            "Analizar la facilidad de mantenimiento y actualización.",
            "Comprobar que la solución permita crecer según las necesidades del proyecto.",
            "Identificar los conocimientos técnicos necesarios para su implementación."
        ]

        observations = [
            f"Cantidad de alternativas evaluadas: {len(alternatives)}.",
            "No se proporcionaron especificaciones técnicas detalladas."
        ]

        analysis = (
            f"El análisis tecnológico de la decisión '{title}' "
            f"busca determinar la viabilidad técnica de las alternativas. "
            f"La descripción evaluada es: {description}. "
            f"El contexto tecnológico debe considerar los recursos disponibles: "
            f"{context}. "
            f"Se deben comparar las alternativas considerando su complejidad, "
            f"infraestructura, mantenimiento y capacidad de crecimiento."
        )

        return self.create_response(
            analysis=analysis,
            recommendations=recommendations,
            observations=observations
        )
