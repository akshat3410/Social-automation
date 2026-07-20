import uuid
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from api.dependencies.auth import get_user_repository
from main import app
from models.user import User
from services.auth_service import AuthService

PASSWORD = "a-strong-password-1"


def make_user(**overrides) -> User:
    user = User(
        email="tester@example.com",
        username="tester",
        hashed_password=AuthService().hash_password(PASSWORD),
        is_active=True,
        is_superuser=False,
    )
    user.id = uuid.uuid4()
    user.created_at = datetime.now(UTC)
    user.updated_at = user.created_at
    for key, value in overrides.items():
        setattr(user, key, value)
    return user


class FakeUserRepo:
    def __init__(self, user: User | None):
        self.user = user

    async def get_by_email(self, email: str):
        return self.user if self.user and self.user.email == email else None

    async def get_by_username(self, username: str):
        return self.user if self.user and self.user.username == username else None

    async def get(self, user_id):
        return self.user if self.user and self.user.id == user_id else None


@pytest.fixture
def client():
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def override_user_repo(user: User | None):
    app.dependency_overrides[get_user_repository] = lambda: FakeUserRepo(user)


def test_health_is_public(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.parametrize(
    "method,path",
    [
        ("get", "/api/v1/content/ideas"),
        ("get", "/api/v1/content/drafts"),
        ("get", "/api/v1/analytics/summary"),
        ("get", "/api/v1/publishing/published"),
        ("get", "/api/v1/prompts"),
        ("get", "/api/v1/auth/me"),
    ],
)
def test_protected_endpoints_require_auth(client, method, path):
    response = getattr(client, method)(path)
    assert response.status_code == 401, f"{path} should require authentication"


def test_login_with_valid_credentials_returns_token(client):
    override_user_repo(make_user())
    response = client.post(
        "/api/v1/auth/login", data={"username": "tester", "password": PASSWORD}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_with_wrong_password_is_rejected(client):
    override_user_repo(make_user())
    response = client.post(
        "/api/v1/auth/login", data={"username": "tester", "password": "wrong-password"}
    )
    assert response.status_code == 401


def test_login_unknown_user_is_rejected(client):
    override_user_repo(None)
    response = client.post(
        "/api/v1/auth/login", data={"username": "ghost", "password": PASSWORD}
    )
    assert response.status_code == 401


def test_login_token_grants_access_to_me(client):
    user = make_user()
    override_user_repo(user)
    token = client.post(
        "/api/v1/auth/login", data={"username": "tester", "password": PASSWORD}
    ).json()["access_token"]

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "tester@example.com"
    assert body["id"] == str(user.id)


def test_inactive_user_cannot_use_token(client):
    user = make_user()
    override_user_repo(user)
    token = client.post(
        "/api/v1/auth/login", data={"username": "tester", "password": PASSWORD}
    ).json()["access_token"]

    user.is_active = False
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_non_superuser_cannot_access_prompts(client):
    user = make_user()
    override_user_repo(user)
    token = client.post(
        "/api/v1/auth/login", data={"username": "tester", "password": PASSWORD}
    ).json()["access_token"]

    response = client.get("/api/v1/prompts", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
