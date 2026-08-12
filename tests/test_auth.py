from datetime import datetime, timezone
from uuid import uuid4

from app.db.models.user import User


def test_register_success(client, monkeypatch):
    user_id = uuid4()

    class FakeService:
        async def create_user(self, data):
            return User(
                id=user_id,
                username=data.username,
                email=data.email,
                hashed_password="hashed-password",
                is_active=True,
                created_at=datetime.now(timezone.utc),
            )

    monkeypatch.setattr(
        "app.api.auth.UserService",
        lambda repository: FakeService(),
    )

    response = client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == str(user_id)
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert data["is_active"] is True


def test_register_duplicate_username(client, monkeypatch):
    from app.services.users import UserAlreadyExistsError

    class FakeService:
        async def create_user(self, data):
            raise UserAlreadyExistsError("Username already exists")

    monkeypatch.setattr(
        "app.api.auth.UserService",
        lambda repository: FakeService(),
    )

    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "new@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Username already exists"
    }


def test_register_duplicate_email(client, monkeypatch):
    from app.services.users import UserAlreadyExistsError

    class FakeService:
        async def create_user(self, data):
            raise UserAlreadyExistsError("Email already exists")

    monkeypatch.setattr(
        "app.api.auth.UserService",
        lambda repository: FakeService(),
    )

    response = client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "email": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Email already exists"
    }


def test_login_success(client, monkeypatch):
    user_id = uuid4()

    user = User(
        id=user_id,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed-password",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )

    class FakeService:
        async def authenticate_user(self, username, password):
            assert username == "testuser"
            assert password == "password123"
            return user

    monkeypatch.setattr(
        "app.api.auth.UserService",
        lambda repository: FakeService(),
    )

    monkeypatch.setattr(
        "app.api.auth.create_access_token",
        lambda subject: "test-access-token",
    )

    response = client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "password123",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "test-access-token",
        "token_type": "bearer",
    }


def test_login_invalid_credentials(client, monkeypatch):
    from app.services.users import InvalidCredentialsError

    class FakeService:
        async def authenticate_user(self, username, password):
            raise InvalidCredentialsError()

    monkeypatch.setattr(
        "app.api.auth.UserService",
        lambda repository: FakeService(),
    )

    response = client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid username or password"
    }


def test_me_success(client):
    user_id = uuid4()

    user = User(
        id=user_id,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed-password",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )

    async def fake_get_current_user():
        return user

    from app.main import app
    from app.core.security import get_current_user

    app.dependency_overrides[get_current_user] = fake_get_current_user

    try:
        response = client.get(
            "/auth/me",
            headers={
                "Authorization": "Bearer test-access-token",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(user_id)
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert data["is_active"] is True


def test_me_without_token(client):
    response = client.get("/auth/me")

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Not authenticated"
    }


def test_me_invalid_token(client):
    response = client.get(
        "/auth/me",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401
