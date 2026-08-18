from datetime import datetime, timezone
from uuid import uuid4

from app.db.models.user import User, UserRole
from app.core.security import get_current_user
from app.main import app


def make_user(role: UserRole) -> User:
    return User(
        id=uuid4(),
        username="testuser",
        email="test@example.com",
        hashed_password="test",
        is_active=True,
        role=role,
        created_at=datetime.now(timezone.utc),
    )


def override_user(role: UserRole):
    async def dependency():
        return make_user(role)

    return dependency

def test_list_users_viewer_forbidden(client):
    app.dependency_overrides[get_current_user] = override_user(
        UserRole.VIEWER
    )

    try:
        response = client.get("/users")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 403


def test_list_users_operator_forbidden(client):
    app.dependency_overrides[get_current_user] = override_user(
        UserRole.OPERATOR
    )

    try:
        response = client.get("/users")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 403


def test_list_users_admin(client, monkeypatch):
    app.dependency_overrides[get_current_user] = override_user(
        UserRole.ADMIN
    )

    class FakeRepository:
        async def get_all(self):
            return [
                make_user(UserRole.ADMIN),
                make_user(UserRole.VIEWER),
            ]

    monkeypatch.setattr(
        "app.api.users.UserRepository",
        lambda db: FakeRepository(),
    )

    try:
        response = client.get("/users")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["role"] == "admin"
    assert data[1]["role"] == "viewer"
