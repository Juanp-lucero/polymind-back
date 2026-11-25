def test_health_reports_database_and_ai(client) -> None:
    body = client.get("/health").json()
    assert body["status"] == "healthy"
    assert body["database"] == "connected"
    assert body["ai_configured"] is False
