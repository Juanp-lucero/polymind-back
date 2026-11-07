
from app.agents.base_agent import BaseAgent


class FinancialAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="Financial Agent",
            description="Analiza costos, presupuesto y viabilidad financiera de las decisiones."
        )

    def analyze(self, decision: dict) -> dict:

        title = decision.get("title", "")
        description = decision.get("description", "")
        context = decision.get("context", "")
        alternatives = decision.get("alternatives", [])

        if not alternatives:
            return self.create_response(
                analysis="No es posible realizar el análisis financiero porque no existen alternativas.",
                recommendations=[
                    "Agregar al menos una alternativa antes de evaluar la decisión."
                ],
                observations=["No se recibieron alternativas."]
            )

        recommendations = [
            "Establecer un presupuesto inicial para cada alternativa.",
            "Identificar los costos de implementación y mantenimiento.",
            "Comparar los beneficios económicos esperados.",
            "Evaluar el retorno de inversión antes de tomar una decisión."
        ]

        observations = [
            f"Cantidad de alternativas evaluadas: {len(alternatives)}.",
            "No se proporcionaron cifras financieras concretas."
        ]

        analysis = (
            f"El análisis financiero de la decisión '{title}' "
            f"se enfoca en identificar los costos, beneficios y "
            f"necesidades presupuestarias de cada alternativa. "
            f"La descripción evaluada es: {description}. "
            f"El contexto empresarial es: {context}. "
            f"Se deben comparar las alternativas para determinar "
            f"cuál ofrece mejores condiciones económicas."
        )

        return self.create_response(
            analysis=analysis,
            recommendations=recommendations,
            observations=observations
        )
