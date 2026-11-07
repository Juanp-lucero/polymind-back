
from app.agents.base_agent import BaseAgent


class RiskAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="Risk Agent",
            description="Evalúa los riesgos y la seguridad de las alternativas."
        )

    def analyze(self, decision: dict) -> dict:

        title = decision.get("title", "")
        description = decision.get("description", "")
        context = decision.get("context", "")
        alternatives = decision.get("alternatives", [])

        if not alternatives:
            return self.create_response(
                analysis="No existen alternativas para evaluar los riesgos.",
                recommendations=["Agregar al menos una alternativa."],
                observations=["No se recibieron alternativas."]
            )

        evaluations = []

        for alternative in alternatives:

            alternative_lower = alternative.lower()
            score = 5
            reasons = []

            # Plataformas comerciales administradas
            if any(word in alternative_lower for word in [
                "shopify",
                "plataforma comercial",
                "contratar"
            ]):
                score += 2
                reasons.append(
                    "Puede reducir ciertos riesgos de infraestructura al utilizar servicios administrados."
                )

            # Código abierto
            if any(word in alternative_lower for word in [
                "woocommerce",
                "código abierto",
                "open source"
            ]):
                score += 1
                reasons.append(
                    "Permite controlar la solución, aunque requiere gestionar actualizaciones y seguridad."
                )

            # Desarrollo propio
            if any(word in alternative_lower for word in [
                "desde cero",
                "desarrollar una plataforma propia"
            ]):
                score -= 1
                reasons.append(
                    "Puede aumentar los riesgos de desarrollo, mantenimiento y errores técnicos."
                )

            score = max(1, min(10, score))

            if not reasons:
                reasons.append(
                    "Se necesitan datos adicionales para identificar y medir los riesgos específicos."
                )

            evaluations.append({
                "alternative": alternative,
                "score": score,
                "justification": " ".join(reasons)
            })

        recommendations = [
            "Establecer mecanismos de protección de datos.",
            "Implementar copias de seguridad periódicas.",
            "Crear planes de contingencia.",
            "Evaluar los riesgos financieros y operativos.",
            "Realizar pruebas de seguridad antes de implementar la solución."
        ]

        scores = [item["score"] for item in evaluations]

        analysis = (
            f"El análisis de riesgos de '{title}' evaluó "
            f"{len(alternatives)} alternativas. "
            f"Se consideraron riesgos técnicos, operativos y de mantenimiento. "
            f"Descripción: {description}. "
            f"Contexto: {context}. "
            f"La puntuación promedio de seguridad fue "
            f"{sum(scores) / len(scores):.2f} sobre 10."
        )

        return self.create_response(
            analysis=analysis,
            recommendations=recommendations,
            observations=[
                "Una puntuación alta representa mejores condiciones estimadas de seguridad.",
                "No se proporcionaron datos históricos ni evaluaciones técnicas de seguridad."
            ],
            alternative_evaluations=evaluations
        )
