"""AI output of the specialist agents is validated before it is used."""

from app.agents import base_agent
from app.agents.financial_agent import FinancialAgent

DECISION = {
    "title": "Tienda en línea",
    "description": "Elegir la plataforma de comercio electrónico.",
    "context": "Presupuesto limitado.",
    "alternatives": ["WooCommerce", "Shopify"],
}


def ai_returns(monkeypatch, data) -> None:
    monkeypatch.setattr(base_agent, "is_ai_configured", lambda: True)
    monkeypatch.setattr(base_agent, "generate_json", lambda *_args, **_kw: data)


def valid_ai_response() -> dict:
    return {
        "analysis": "WooCommerce reduce costos de licencia; Shopify cobra mensualidad.",
        "alternative_evaluations": [
            {"alternative": "WooCommerce", "score": 8, "justification": "Sin licencia."},
            {"alternative": "Shopify", "score": 6, "justification": "Pago mensual."},
        ],
        "recommendations": ["Pedir cotización de hosting."],
        "missing_information": ["Volumen de ventas esperado."],
    }


def test_valid_ai_evaluation_is_used(monkeypatch) -> None:
    ai_returns(monkeypatch, valid_ai_response())
    result = FinancialAgent().analyze(DECISION)

    scores = {item["alternative"]: item["score"] for item in result["alternative_evaluations"]}
    assert scores == {"WooCommerce": 8.0, "Shopify": 6.0}
    assert "Evaluación generada con IA (Groq) y validada." in result["observations"]
    assert any("Volumen de ventas" in item for item in result["observations"])


def test_scores_are_clamped_between_1_and_10(monkeypatch) -> None:
    data = valid_ai_response()
    data["alternative_evaluations"][0]["score"] = 15
    data["alternative_evaluations"][1]["score"] = -3
    ai_returns(monkeypatch, data)

    result = FinancialAgent().analyze(DECISION)
    scores = [item["score"] for item in result["alternative_evaluations"]]
    assert scores == [10.0, 1.0]


def test_missing_alternative_falls_back_to_rules(monkeypatch) -> None:
    data = valid_ai_response()
    data["alternative_evaluations"].pop()
    ai_returns(monkeypatch, data)

    result = FinancialAgent().analyze(DECISION)
    assert any("reglas heurísticas" in item for item in result["observations"])
    assert len(result["alternative_evaluations"]) == 2


def test_empty_justification_falls_back_to_rules(monkeypatch) -> None:
    data = valid_ai_response()
    data["alternative_evaluations"][1]["justification"] = "   "
    ai_returns(monkeypatch, data)

    result = FinancialAgent().analyze(DECISION)
    assert any("reglas heurísticas" in item for item in result["observations"])


def test_provider_failure_falls_back_to_rules(monkeypatch) -> None:
    ai_returns(monkeypatch, None)
    result = FinancialAgent().analyze(DECISION)
    assert any("reglas heurísticas" in item for item in result["observations"])


def test_invented_alternatives_are_ignored(monkeypatch) -> None:
    data = valid_ai_response()
    data["alternative_evaluations"].append(
        {"alternative": "Magento", "score": 9, "justification": "No pedida."}
    )
    ai_returns(monkeypatch, data)

    result = FinancialAgent().analyze(DECISION)
    alternatives = [item["alternative"] for item in result["alternative_evaluations"]]
    assert alternatives == ["WooCommerce", "Shopify"]
