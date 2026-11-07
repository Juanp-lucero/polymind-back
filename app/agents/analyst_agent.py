
from app.agents.base_agent import BaseAgent


class AnalystAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="Analyst Agent",
            description="Integra los resultados de los agentes especializados y genera un informe general."
        )

    def analyze(self, decision: dict) -> dict:

        return self.create_response(
            analysis="El analista necesita los resultados de los agentes especializados.",
            recommendations=[
                "Ejecutar primero los agentes especializados.",
                "Enviar sus resultados al analista para generar el informe."
            ],
            observations=["No se recibieron resultados de otros agentes."]
        )

    def generate_report(self, decision: dict, agent_results: list[dict]) -> dict:

        if not agent_results:
            return self.create_response(
                analysis="No existen resultados para generar un informe.",
                recommendations=[
                    "Ejecutar los agentes especializados antes de generar el informe."
                ],
                observations=["Lista de resultados vacía."]
            )

        title = decision.get("title", "Decisión sin título")

        analyses = []
        recommendations = []
        observations = []

        for result in agent_results:

            agent_name = result.get("agent", "Agente desconocido")
            analysis = result.get("analysis", "")

            analyses.append(
                f"{agent_name}: {analysis}"
            )

            for recommendation in result.get("recommendations", []):
                recommendations.append(
                    f"[{agent_name}] {recommendation}"
                )

            for observation in result.get("observations", []):
                observations.append(
                    f"[{agent_name}] {observation}"
                )

        final_analysis = (
            f"INFORME GENERAL DE POLYMIND IA\n\n"
            f"Decisión evaluada: {title}\n\n"
            + "\n\n".join(analyses)
            + "\n\nCONCLUSIÓN:\n"
            "La decisión debe evaluarse considerando conjuntamente "
            "los aspectos financieros, tecnológicos, humanos y de riesgos. "
            "La alternativa más conveniente deberá equilibrar estos factores."
        )

        return self.create_response(
            analysis=final_analysis,
            recommendations=recommendations,
            observations=observations
        )
