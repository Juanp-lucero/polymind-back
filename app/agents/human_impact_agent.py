
from app.agents.base_agent import BaseAgent


class HumanImpactAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="Human Impact Agent",
            description="Evalúa las consecuencias humanas y sociales de las decisiones."
        )

    def analyze(self, decision: dict) -> dict:

        title = decision.get("title", "")
        description = decision.get("description", "")
        context = decision.get("context", "")
        alternatives = decision.get("alternatives", [])

        if not alternatives:
            return self.create_response(
                analysis="No existen alternativas para evaluar el impacto humano.",
                recommendations=["Agregar al menos una alternativa."],
                observations=["No se recibieron alternativas."]
            )

        context_lower = context.lower()
        evaluations = []

        for alternative in alternatives:

            alternative_lower = alternative.lower()
            score = 5
            reasons = []

            # Facilidad de uso y adaptación
            if any(word in alternative_lower for word in [
                "shopify",
                "plataforma comercial",
                "contratar"
            ]):
                score += 2
                reasons.append(
                    "Puede facilitar la adopción gracias a herramientas listas para utilizar."
                )

            # Flexibilidad y adaptación
            if any(word in alternative_lower for word in [
                "código abierto",
                "woocommerce",
                "open source"
            ]):
                score += 1
                reasons.append(
                    "Permite adaptar la experiencia a las necesidades de los usuarios."
                )

            # Necesidad de desarrollo especializado
            if any(word in alternative_lower for word in [
                "desde cero",
                "desarrollar una plataforma propia"
            ]):
                score -= 1
                reasons.append(
                    "Puede requerir más tiempo de capacitación y adaptación."
                )

            if any(word in context_lower for word in [
                "pocos empleados",
                "personal reducido"
            ]):
                if any(word in alternative_lower for word in [
                    "desde cero",
                    "desarrollar una plataforma propia"
                ]):
                    score -= 1
                    reasons.append(
                        "Un equipo pequeño podría tener dificultades para asumir el desarrollo y mantenimiento."
                    )

            score = max(1, min(10, score))

            if not reasons:
                reasons.append(
                    "Se necesita información adicional sobre las necesidades de empleados y usuarios."
                )

            evaluations.append({
                "alternative": alternative,
                "score": score,
                "justification": " ".join(reasons)
            })

        recommendations = [
            "Capacitar a los empleados para utilizar la nueva solución.",
            "Evaluar la facilidad de uso para los clientes.",
            "Considerar las necesidades de accesibilidad.",
            "Analizar los cambios en los procesos de trabajo.",
            "Recopilar opiniones de los usuarios antes de implementar la solución."
        ]

        scores = [item["score"] for item in evaluations]

        analysis = (
            f"El análisis de impacto humano de '{title}' evaluó "
            f"{len(alternatives)} alternativas. "
            f"Se consideraron aspectos de adaptación, facilidad de uso "
            f"y necesidades de las personas involucradas. "
            f"Descripción: {description}. "
            f"Contexto: {context}. "
            f"Puntuación promedio: {sum(scores) / len(scores):.2f} sobre 10."
        )

        return self.create_response(
            analysis=analysis,
            recommendations=recommendations,
            observations=[
                "Las puntuaciones son estimaciones basadas en reglas.",
                "No se proporcionaron encuestas ni datos directos de los usuarios."
            ],
            alternative_evaluations=evaluations
        )
