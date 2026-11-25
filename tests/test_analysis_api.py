"""End-to-end analysis: FastAPI -> gRPC client (in-process) -> agents -> DB."""

from tests.test_decisions import create_decision


def run_analysis(client, headers, decision_id: int):
    return client.post(f"/decisions/{decision_id}/analyze", headers=headers)


def test_analysis_is_saved_with_agent_details(client, auth_headers) -> None:
    decision = create_decision(client, auth_headers)

    response = run_analysis(client, auth_headers, decision["id"])
    assert response.status_code == 200, response.text
    analysis = response.json()
    assert analysis["status"] == "completed"
    assert analysis["recommendations"]

    complete = client.get(
        f"/decisions/{decision['id']}/analyses/{analysis['id']}/complete",
        headers=auth_headers,
    ).json()

    agents = [item["agent"] for item in complete["agent_results"]]
    assert agents == [
        "Financial Agent",
        "Technology Agent",
        "Human Impact Agent",
        "Risk Agent",
    ]
    ranked = [item["alternative"] for item in complete["alternative_comparison"]]
    assert sorted(ranked) == ["Shopify", "WooCommerce"]
    assert abs(sum(complete["weights"].values()) - 1.0) < 1e-6


def test_analysis_history_is_listed(client, auth_headers) -> None:
    decision = create_decision(client, auth_headers)
    run_analysis(client, auth_headers, decision["id"])
    run_analysis(client, auth_headers, decision["id"])

    history = client.get(
        f"/decisions/{decision['id']}/analyses", headers=auth_headers
    ).json()
    assert len(history) == 2


def test_analysis_requires_alternatives(client, auth_headers) -> None:
    decision = create_decision(client, auth_headers, alternatives=[])
    response = run_analysis(client, auth_headers, decision["id"])
    assert response.status_code == 400


def test_cannot_analyze_decisions_of_other_users(client, auth_headers) -> None:
    from tests.conftest import register_and_login

    decision = create_decision(client, auth_headers)
    other = register_and_login(client, email="luis@example.com")
    assert run_analysis(client, other, decision["id"]).status_code == 404
