from app.agents.analyst_agent import AnalystAgent
from app.agents.orchestrator import Orchestrator

DECISION = {
    "title": "Tienda en línea",
    "description": "Elegir la plataforma de comercio electrónico para vender en línea "
                   "a clientes nacionales durante el próximo año.",
    "context": "Presupuesto limitado y equipo pequeño.",
    "alternatives": ["WooCommerce open source", "Shopify comercial"],
}


def comparison_item(alternative, financial, technology, human, risk) -> dict:
    return {
        "alternative": alternative,
        "criteria": {
            "Financial Agent": financial,
            "Technology Agent": technology,
            "Human Impact Agent": human,
            "Risk Agent": risk,
        },
        "weighted_score": 0,
    }


def test_orchestrator_runs_every_specialist() -> None:
    result = Orchestrator().analyze_decision(DECISION)
    assert result["status"] == "completed"
    assert result["total_agents"] == 4
    assert len(result["final_report"]["alternative_evaluations"]) == 2


def test_orchestrator_recovers_when_an_agent_fails() -> None:
    orchestrator = Orchestrator()

    def broken(_decision):
        raise RuntimeError("fallo simulado")

    orchestrator.risk_agent.analyze = broken
    result = orchestrator.analyze_decision(DECISION)

    risk = next(item for item in result["agent_results"] if item["agent"] == "Risk Agent")
    assert "Se recuperó con reglas tras un error del agente." in risk["observations"]
    assert result["status"] == "completed"


def test_weighted_ranking_puts_the_best_alternative_first() -> None:
    result = Orchestrator().analyze_decision(DECISION)
    scores = [
        item["weighted_score"]
        for item in result["final_report"]["alternative_evaluations"]
    ]
    assert scores == sorted(scores, reverse=True)


def test_analyst_detects_strong_disagreements() -> None:
    disagreements = AnalystAgent().find_disagreements([
        comparison_item("A", 9, 8, 7, 3),
        comparison_item("B", 6, 6, 5, 5),
    ])
    assert list(disagreements) == ["A"]
    assert "Financial Agent" in disagreements["A"]
    assert "Risk Agent" in disagreements["A"]


def test_analyst_flags_insufficient_information() -> None:
    gaps = AnalystAgent().find_information_gaps(
        {"description": "Corta", "context": "", "alternatives": ["Única"]}
    )
    assert len(gaps) == 3


def test_analyst_accepts_complete_information() -> None:
    assert AnalystAgent().find_information_gaps(DECISION) == []
