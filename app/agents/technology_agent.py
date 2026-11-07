
from app.agents.base_agent import BaseAgent


class TechnologyAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="Technology Agent",
            description="Evalúa la viabilidad, infraestructura y escalabilidad tecnológica de las alternativas."
        )

    def analyze(self, decision: dict) -> dict:

        title = decision.get("title", "")
        description = decision.get("description", "")
        context = decision.get("context", "")
        alternatives = decision.get("alternatives", [])

        if not alternatives:
            return self.create_response(
                analysis="No existen alternativas para realizar la evaluación tecnológica.",
                recommendations=[
                    "Agregar al menos una alternativa."
                ],
                observations=["No se recibieron alternativas."]
            )

        evaluations = []

        for alternative in alternatives:

            alternative_lower = alternative.lower()

            score = 5
            reasons = []

            # Evaluar soluciones de código abierto
            if any(word in alternative_lower for word in [
                "código abierto",
                "open source",
                "woocommerce"
            ]):
                score += 2
                reasons.append(
                    "Permite personalizar la solución y acceder a su código fuente."
                )

            # Evaluar plataformas comerciales
            if any(word in alternative_lower for word in [
                "shopify",
                "plataforma comercial",
                "contratar"
            ]):
                score += 2
                reasons.append(
                    "Puede ofrecer infraestructura administrada y herramientas listas para utilizar."
                )

            # Evaluar desarrollo propio
            if any(word in alternative_lower for word in [
                "desde cero",
                "desarrollar una plataforma propia"
            ]):
                score -= 1
                reasons.append(
                    "Requiere mayor esfuerzo de desarrollo, pruebas y mantenimiento."
                )

            score = max(1, min(10, score))

            if not reasons:
                reasons.append(
                    "Se necesitan más detalles sobre infraestructura, tecnologías y recursos técnicos."
                )

            evaluations.append({
                "alternative": alternative,
                "score": score,
                "justification": " ".join(reasons)
            })

        recommendations = [
            "Verificar que la tecnología seleccionada permita escalar el sistema.",
            "Evaluar la seguridad y protección de los datos.",
            "Comprobar la compatibilidad con los sistemas existentes.",
            "Analizar los costos de mantenimiento y actualización.",
            "Identificar los conocimientos técnicos necesarios para administrar la solución."
        ]

        scores = [
            item["score"] for item in evaluations
        ]

        analysis = (
            f"El análisis tecnológico de '{title}' evaluó "
            f"{len(alternatives)} alternativas. "
            f"Se consideraron aspectos de personalización, "
            f"infrastructura, mantenimiento y escalabilidad. "
            f"La descripción de la decisión es: {description}. "
            f"El contexto disponible es: {context}. "
            f"La puntuación tecnológica promedio fue "
            f"{sum(scores) / len(scores):.2f} sobre 10."
        )

        return self.create_response(
            analysis=analysis,
            recommendations=recommendations,
            observations=[
                "Las puntuaciones son estimaciones preliminares basadas en reglas.",
                "No se proporcionaron especificaciones técnicas detalladas."
            ],
            alternative_evaluations=evaluations
        )
