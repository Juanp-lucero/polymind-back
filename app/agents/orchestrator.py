
from app.agents.financial_agent import FinancialAgent
from app.agents.technology_agent import TechnologyAgent
from app.agents.human_impact_agent import HumanImpactAgent
from app.agents.risk_agent import RiskAgent
from app.agents.analyst_agent import AnalystAgent


class Orchestrator:

    def __init__(self):

        self.financial_agent = FinancialAgent()
        self.technology_agent = TechnologyAgent()
        self.human_impact_agent = HumanImpactAgent()
        self.risk_agent = RiskAgent()
        self.analyst_agent = AnalystAgent()

    def analyze_decision(self, decision: dict) -> dict:

        agents = [
            self.financial_agent,
            self.technology_agent,
            self.human_impact_agent,
            self.risk_agent
        ]

        agent_results = []

        for agent in agents:

            result = agent.analyze(decision)

            agent_results.append(result)

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
