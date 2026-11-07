
from app.agents.base_agent import BaseAgent


class AnalystAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="Analyst Agent",
            description="Compara las evaluaciones y determina la alternativa mejor calificada."
        )

        self.weights = {
            "Financial Agent": 0.30,
            "Technology Agent": 0.30,
            "Human Impact Agent": 0.20,
            "Risk Agent": 0.20
        }

    def analyze(self, decision: dict) -> dict:

        return self.create_response(
            analysis="El analista necesita las evaluaciones de los agentes especializados.",
            recommendations=[
                "Ejecutar los agentes especializados antes de generar el informe."
            ],
            observations=["No se recibieron evaluaciones."]
        )

    def generate_report(
        self,
        decision: dict,
        agent_results: list[dict]
    ) -> dict:

        alternatives = decision.get("alternatives", [])

        if not alternatives or not agent_results:
            return self.create_response(
                analysis="No hay suficientes datos para comparar las alternativas.",
                recommendations=["Completar las evaluaciones de los agentes."],
                observations=["Faltan alternativas o resultados."]
            )

        agent_scores = {}

        for result in agent_results:

            agent_name = result.get("agent")

            if agent_name not in self.weights:
                continue

            evaluations = {
                item["alternative"]: item["score"]
                for item in result.get("alternative_evaluations", [])
            }

            agent_scores[agent_name] = evaluations

        missing_agents = [
            name for name in self.weights
            if name not in agent_scores
        ]

        if missing_agents:
            raise ValueError(
                f"Missing agent evaluations: {missing_agents}"
            )

        comparison = []

        for alternative in alternatives:

            weighted_score = 0
            criteria = {}

            for agent_name, weight in self.weights.items():

                score = agent_scores[agent_name].get(alternative)

                if score is None:
                    raise ValueError(
                        f"Missing score for {alternative} from {agent_name}"
                    )

                if not isinstance(score, (int, float)) or not 1 <= score <= 10:
                    raise ValueError(
                        f"Invalid score for {alternative} from {agent_name}"
                    )

                criteria[agent_name] = score
                weighted_score += score * weight

            comparison.append({
                "alternative": alternative,
                "criteria": criteria,
                "weighted_score": round(weighted_score, 2)
            })

        comparison.sort(
            key=lambda item: item["weighted_score"],
            reverse=True
        )

        winner = comparison[0]

        recommendations = [
            (
                f"{item['alternative']}: "
                f"puntuación ponderada de {item['weighted_score']}/10."
            )
            for item in comparison
        ]

        final_analysis = (
            f"INFORME COMPARATIVO DE POLYMIND IA\n\n"
            f"Decisión evaluada: {decision.get('title')}\n\n"
            f"Se evaluaron {len(alternatives)} alternativas "
            f"mediante cuatro criterios especializados.\n\n"
            f"Ponderaciones utilizadas:\n"
            f"- Financiero: 30%\n"
            f"- Tecnológico: 30%\n"
            f"- Impacto humano: 20%\n"
            f"- Riesgos: 20%\n\n"
            f"ALTERNATIVA MEJOR CALIFICADA:\n"
            f"{winner['alternative']}\n"
            f"Puntuación: {winner['weighted_score']}/10.\n\n"
            f"La alternativa seleccionada obtuvo la mayor puntuación "
            f"ponderada según las evaluaciones recibidas. "
            f"Esta recomendación es preliminar y depende de la calidad "
            f"de los datos proporcionados."
        )

        return self.create_response(
            analysis=final_analysis,
            recommendations=recommendations,
            observations=[
                "Las puntuaciones provienen de reglas heurísticas.",
                "Los pesos representan criterios definidos para el proyecto.",
                "La alternativa mejor calificada no representa una garantía de éxito."
            ],
            alternative_evaluations=comparison
        )
