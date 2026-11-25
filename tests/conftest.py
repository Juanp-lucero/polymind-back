"""Shared fixtures: a temporary SQLite database and no calls to Groq."""

import os
import tempfile

# Configure the environment before the application modules are imported.
_DB_FILE = os.path.join(tempfile.mkdtemp(prefix="polymind-tests-"), "test.db")
os.environ["DATABASE_URL"] = f"sqlite:///{_DB_FILE}"
os.environ.setdefault("SECRET_KEY", "test-secret-key-only-for-pytest")
os.environ["GROQ_API_KEY"] = ""
os.environ["GRPC_MODE"] = "inprocess"

from collections.abc import Generator  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.core.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.services import groq_service  # noqa: E402


@pytest.fixture(autouse=True)
def no_groq(monkeypatch) -> None:
    """Tests never reach the real AI provider."""
    monkeypatch.setattr(groq_service, "GROQ_API_KEY", "")


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


def register_and_login(
    client: TestClient,
    email: str = "ana@example.com",
    password: str = "Secret123!",
) -> dict[str, str]:
    """Create a user and return the Authorization header."""
    response = client.post(
        "/auth/register",
        json={"name": "Ana", "email": email, "password": password},
    )
    assert response.status_code == 201, response.text
    response = client.post(
        "/auth/login", json={"email": email, "password": password}
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    return register_and_login(client)
