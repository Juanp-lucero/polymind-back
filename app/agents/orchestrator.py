import logging
from concurrent.futures import ThreadPoolExecutor

from app.agents.financial_agent import FinancialAgent
from app.agents.technology_agent import TechnologyAgent
from app.agents.human_impact_agent import HumanImpactAgent
from app.agents.risk_agent import RiskAgent
from app.agents.analyst_agent import AnalystAgent

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Coordina el análisis multiagente.

    1. Los cuatro agentes especialistas evalúan la decisión en paralelo,
       cada uno desde su perspectiva (con IA y, si no es posible, con reglas).
    2. Si un agente falla, se usa su evaluación por reglas para que el
       análisis completo no se pierda.
    3. El agente analista consolida, pondera y redacta el informe final.
    """

    def __init__(self):

        self.financial_agent = FinancialAgent()
        self.technology_agent = TechnologyAgent()
        self.human_impact_agent = HumanImpactAgent()
        self.risk_agent = RiskAgent()
        self.analyst_agent = AnalystAgent()

    @property
    def specialist_agents(self) -> list:
        return [
            self.financial_agent,
            self.technology_agent,
            self.human_impact_agent,
            self.risk_agent
        ]

    def _run_agent(self, agent, decision: dict) -> dict:
        try:
            return agent.analyze(decision)
        except Exception:
            logger.exception(
                "%s falló; se usará su evaluación por reglas.", agent.name
            )
            result = agent.rule_based_analyze(decision)
            result.setdefault("observations", []).append(
                "Se recuperó con reglas tras un error del agente."
            )
            return result

    def analyze_decision(self, decision: dict) -> dict:

        agents = self.specialist_agents

        with ThreadPoolExecutor(max_workers=len(agents)) as executor:
            agent_results = list(
                executor.map(
                    lambda agent: self._run_agent(agent, decision),
                    agents
                )
            )

        final_report = self.analyst_agent.generate_report(
            decision,
            agent_results
        )

        return {
            "decision": decision.get("title"),
            "status": "completed",
            "total_agents": len(agents),
            "agent_results": agent_results,
            "final_report": final_report
        }
