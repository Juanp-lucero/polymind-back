from tests.conftest import register_and_login
from tests.test_decisions import create_decision


def test_stats_start_empty(client, auth_headers) -> None:
    stats = client.get("/stats/", headers=auth_headers).json()
    assert stats["total_decisions"] == 0
    assert stats["total_analyses"] == 0


def test_stats_count_only_the_user_data(client, auth_headers) -> None:
    decision = create_decision(client, auth_headers)
    client.post(f"/decisions/{decision['id']}/analyze", headers=auth_headers)

    stats = client.get("/stats/", headers=auth_headers).json()
    assert stats["total_decisions"] == 1
    assert stats["total_analyses"] == 1
    assert stats["top_recommendations"]

    other = register_and_login(client, email="luis@example.com")
    other_stats = client.get("/stats/", headers=other).json()
    assert other_stats["total_decisions"] == 0
    assert other_stats["total_analyses"] == 0
