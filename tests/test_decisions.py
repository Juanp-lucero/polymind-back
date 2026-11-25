from tests.conftest import register_and_login

DECISION = {
    "title": "Plataforma de comercio electrónico",
    "description": "Elegir la plataforma para la tienda en línea de la empresa.",
    "context": "Presupuesto limitado y un equipo técnico pequeño.",
    "alternatives": ["WooCommerce", "Shopify"],
}


def create_decision(client, headers, **overrides) -> dict:
    response = client.post(
        "/decisions/", json={**DECISION, **overrides}, headers=headers
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_create_and_list_decisions(client, auth_headers) -> None:
    created = create_decision(client, auth_headers)
    assert created["status"] == "pending"
    assert created["alternatives"] == ["WooCommerce", "Shopify"]

    listed = client.get("/decisions/", headers=auth_headers).json()
    assert [item["id"] for item in listed] == [created["id"]]


def test_alternatives_are_normalized(client, auth_headers) -> None:
    created = create_decision(
        client, auth_headers, alternatives=[" Shopify ", "shopify", "", "Wix"]
    )
    assert created["alternatives"] == ["Shopify", "Wix"]


def test_update_and_delete_decision(client, auth_headers) -> None:
    created = create_decision(client, auth_headers)

    response = client.put(
        f"/decisions/{created['id']}",
        json={"title": "Nueva plataforma", "status": "in_progress"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Nueva plataforma"
    assert response.json()["status"] == "in_progress"

    assert client.delete(
        f"/decisions/{created['id']}", headers=auth_headers
    ).status_code == 200
    assert client.get(
        f"/decisions/{created['id']}", headers=auth_headers
    ).status_code == 404


def test_users_cannot_access_decisions_of_others(client, auth_headers) -> None:
    created = create_decision(client, auth_headers)
    other = register_and_login(client, email="luis@example.com")

    assert client.get(f"/decisions/{created['id']}", headers=other).status_code == 404
    assert client.put(
        f"/decisions/{created['id']}", json={"title": "Hackeo"}, headers=other
    ).status_code == 404
    assert client.delete(f"/decisions/{created['id']}", headers=other).status_code == 404
    assert client.get("/decisions/", headers=other).json() == []


def test_invalid_payload_is_rejected(client, auth_headers) -> None:
    response = client.post(
        "/decisions/",
        json={**DECISION, "title": "x", "description": "corta"},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_decisions_require_authentication(client) -> None:
    assert client.get("/decisions/").status_code in (401, 403)
