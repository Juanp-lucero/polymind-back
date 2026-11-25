from tests.conftest import register_and_login


def test_register_rejects_duplicate_email(client) -> None:
    register_and_login(client)
    response = client.post(
        "/auth/register",
        json={"name": "Otra", "email": "ana@example.com", "password": "Secret123!"},
    )
    assert response.status_code == 400


def test_login_with_wrong_password_is_rejected(client) -> None:
    register_and_login(client)
    response = client.post(
        "/auth/login", json={"email": "ana@example.com", "password": "incorrecta"}
    )
    assert response.status_code == 401


def test_me_returns_the_authenticated_user(client, auth_headers) -> None:
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "ana@example.com"
    assert "password" not in response.json()


def test_me_requires_a_token(client) -> None:
    assert client.get("/auth/me").status_code in (401, 403)


def test_refresh_token_returns_a_new_access_token(client) -> None:
    client.post(
        "/auth/register",
        json={"name": "Ana", "email": "ana@example.com", "password": "Secret123!"},
    )
    tokens = client.post(
        "/auth/login", json={"email": "ana@example.com", "password": "Secret123!"}
    ).json()

    response = client.post(
        "/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert response.status_code == 200
    new_token = response.json()["access_token"]
    assert client.get(
        "/auth/me", headers={"Authorization": f"Bearer {new_token}"}
    ).status_code == 200


def test_access_token_cannot_be_used_as_refresh_token(client) -> None:
    client.post(
        "/auth/register",
        json={"name": "Ana", "email": "ana@example.com", "password": "Secret123!"},
    )
    tokens = client.post(
        "/auth/login", json={"email": "ana@example.com", "password": "Secret123!"}
    ).json()

    response = client.post(
        "/auth/refresh", json={"refresh_token": tokens["access_token"]}
    )
    assert response.status_code == 401
