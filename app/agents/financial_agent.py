
from app.agents.base_agent import BaseAgent


class FinancialAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="Financial Agent",
            description="Evalúa costos, presupuesto y viabilidad financiera de las alternativas."
        )

    def analyze(self, decision: dict) -> dict:

        title = decision.get("title", "")
        description = decision.get("description", "")
        context = decision.get("context", "")
        alternatives = decision.get("alternatives", [])

        if not alternatives:
            return self.create_response(
                analysis="No existen alternativas para realizar la evaluación financiera.",
                recommendations=[
                    "Agregar al menos una alternativa."
                ],
                observations=["No se recibieron alternativas."]
            )

        context_lower = context.lower()
        evaluations = []

        limited_budget = any(
            word in context_lower
            for word in ["presupuesto limitado", "pocos recursos", "bajo presupuesto"]
        )

        for alternative in alternatives:

            alternative_lower = alternative.lower()

            score = 5
            reasons = []

            if limited_budget:
                if any(word in alternative_lower for word in [
                    "código abierto",
                    "open source",
                    "woocommerce",
                    "gratuita",
                    "propia"
                ]):
                    score += 2
                    reasons.append(
                        "Puede ofrecer mayor control sobre los costos iniciales."
                    )

                if any(word in alternative_lower for word in [
                    "contratar",
                    "suscripción",
                    "comercial",
                    "shopify"
                ]):
                    score -= 1
                    reasons.append(
                        "Puede implicar pagos recurrentes o costos de contratación."
                    )

            if any(word in alternative_lower for word in [
                "desde cero",
                "desarrollar una plataforma propia"
            ]):
                score -= 1
                reasons.append(
                    "Puede requerir una inversión inicial mayor en desarrollo y mantenimiento."
                )

            score = max(1, min(10, score))

            if not reasons:
                reasons.append(
                    "Se necesita información sobre costos de implementación y mantenimiento para evaluar mejor esta alternativa."
                )

            evaluations.append({
                "alternative": alternative,
                "score": score,
                "justification": " ".join(reasons)
            })

        recommendations = [
            "Solicitar cotizaciones para conocer los costos reales de cada alternativa.",
            "Comparar los gastos iniciales y los costos de mantenimiento.",
            "Estimar los ingresos esperados y el retorno de inversión.",
            "Considerar los costos adicionales de capacitación e infraestructura."
        ]

        scores = [
            evaluation["score"]
            for evaluation in evaluations
        ]

        analysis = (
            f"El análisis financiero de '{title}' evaluó "
            f"{len(alternatives)} alternativas. "
            f"Las puntuaciones se basan en las características "
            f"descritas y en el contexto presupuestario disponible. "
            f"La descripción de la decisión es: {description}. "
            f"La puntuación promedio obtenida fue "
            f"{sum(scores) / len(scores):.2f} sobre 10."
        )

        return self.create_response(
            analysis=analysis,
            recommendations=recommendations,
            observations=[
                "Las puntuaciones son estimaciones preliminares basadas en reglas.",
                "No se proporcionaron cifras reales de inversión, ingresos o mantenimiento."
            ],
            alternative_evaluations=evaluations
        )
