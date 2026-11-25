"""The rule-based evaluation is the safety net when AI is unavailable."""

import pytest

from app.agents.financial_agent import FinancialAgent
from app.agents.human_impact_agent import HumanImpactAgent
from app.agents.risk_agent import RiskAgent
from app.agents.technology_agent import TechnologyAgent

DECISION = {
    "title": "Tienda en línea",
    "description": "Elegir la plataforma de comercio electrónico.",
    "context": "Presupuesto limitado.",
    "alternatives": ["WooCommerce open source", "Shopify comercial"],
}

AGENTS = [FinancialAgent, TechnologyAgent, HumanImpactAgent, RiskAgent]


@pytest.mark.parametrize("agent_class", AGENTS)
def test_every_alternative_gets_a_justified_score(agent_class) -> None:
    result = agent_class().analyze(DECISION)

    assert [item["alternative"] for item in result["alternative_evaluations"]] == (
        DECISION["alternatives"]
    )
    for item in result["alternative_evaluations"]:
        assert 1 <= item["score"] <= 10
        assert item["justification"].strip()


@pytest.mark.parametrize("agent_class", AGENTS)
def test_without_ai_the_rules_are_reported(agent_class) -> None:
    result = agent_class().analyze(DECISION)
    assert any("reglas heurísticas" in item for item in result["observations"])


@pytest.mark.parametrize("agent_class", AGENTS)
def test_no_alternatives_returns_guidance(agent_class) -> None:
    result = agent_class().analyze({**DECISION, "alternatives": []})
    assert result["alternative_evaluations"] == []
    assert result["recommendations"]


def test_limited_budget_favors_open_source_financially() -> None:
    result = FinancialAgent().analyze(DECISION)
    scores = {item["alternative"]: item["score"] for item in result["alternative_evaluations"]}
    assert scores["WooCommerce open source"] > scores["Shopify comercial"]
