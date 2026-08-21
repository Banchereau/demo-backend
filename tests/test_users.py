from datetime import datetime, timezone
from uuid import uuid4

from app.db.models.user import User, UserRole
from app.core.security import get_current_user
from app.main import app
from app.services.users import (
    UserNotFoundError,
    UserSelfDeletionError,
)

def make_user(role: UserRole) -> User:
    return User(
        id=uuid4(),
        username="testuser",
        email="test@example.com",
        hashed_password="test",
        is_active=True,
        role=role,
        must_change_password=False,
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


def test_create_user_viewer_forbidden(client):
    app.dependency_overrides[get_current_user] = override_user(
        UserRole.VIEWER
    )

    try:
        response = client.post(
            "/users",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123",
                "role": "viewer",
            },
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 403


def test_create_user_operator_forbidden(client):
    app.dependency_overrides[get_current_user] = override_user(
        UserRole.OPERATOR
    )

    try:
        response = client.post(
            "/users",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123",
                "role": "viewer",
            },
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 403


def test_create_user_admin(client, monkeypatch):
    app.dependency_overrides[get_current_user] = override_user(
        UserRole.ADMIN
    )

    user = make_user(UserRole.OPERATOR)
    user.username = "newuser"
    user.email = "newuser@example.com"
    user.must_change_password = True

    class FakeService:
        async def create_user(
            self,
            data,
            force_password_change=False,
        ):
            assert data.username == "newuser"
            assert data.email == "newuser@example.com"
            assert data.role == UserRole.OPERATOR
            assert force_password_change is True
            return user

    monkeypatch.setattr(
        "app.api.users.UserService",
        lambda repository: FakeService(),
    )

    try:
        response = client.post(
            "/users",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123",
                "role": "operator",
            },
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert data["role"] == "operator"
    assert data["must_change_password"] is True


def test_delete_user_viewer_forbidden(client):
    app.dependency_overrides[get_current_user] = override_user(
        UserRole.VIEWER
    )

    try:
        response = client.delete(f"/users/{uuid4()}")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 403


def test_delete_user_operator_forbidden(client):
    app.dependency_overrides[get_current_user] = override_user(
        UserRole.OPERATOR
    )

    try:
        response = client.delete(f"/users/{uuid4()}")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 403


def test_delete_user_admin_success(client, monkeypatch):
    current_user = make_user(UserRole.ADMIN)
    target_user = make_user(UserRole.VIEWER)

    app.dependency_overrides[get_current_user] = (
        lambda: current_user
    )

    class FakeService:
        async def delete_user(
            self,
            user_id,
            current_user,
        ):
            assert user_id == target_user.id
            assert current_user.id == current_user.id

    monkeypatch.setattr(
        "app.api.users.UserService",
        lambda repository: FakeService(),
    )

    try:
        response = client.delete(
            f"/users/{target_user.id}"
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 204


def test_delete_user_not_found(client, monkeypatch):
    current_user = make_user(UserRole.ADMIN)
    user_id = uuid4()

    app.dependency_overrides[get_current_user] = (
        lambda: current_user
    )

    class FakeService:
        async def delete_user(
            self,
            user_id,
            current_user,
        ):
            raise UserNotFoundError("User not found")

    monkeypatch.setattr(
        "app.api.users.UserService",
        lambda repository: FakeService(),
    )

    try:
        response = client.delete(
            f"/users/{user_id}"
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_delete_user_self_forbidden(client, monkeypatch):
    current_user = make_user(UserRole.ADMIN)

    app.dependency_overrides[get_current_user] = (
        lambda: current_user
    )

    class FakeService:
        async def delete_user(
            self,
            user_id,
            current_user,
        ):
            raise UserSelfDeletionError(
                "You cannot delete your own account"
            )

    monkeypatch.setattr(
        "app.api.users.UserService",
        lambda repository: FakeService(),
    )

    try:
        response = client.delete(
            f"/users/{current_user.id}"
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "You cannot delete your own account"
    )
