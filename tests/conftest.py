import pytest
from fastapi.testclient import TestClient

from app.core.security import (
    get_current_user,
    get_current_user_ws,
)
from app.db.models.user import User
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def authenticated_client():
    async def override_get_current_user():
        return User(
            username="testuser",
            email="test@example.com",
            hashed_password="test",
            is_active=True,
        )

    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def authenticated_ws_client():
    async def override_get_current_user_ws():
        return User(
            username="testuser",
            email="test@example.com",
            hashed_password="test",
            is_active=True,
        )

    app.dependency_overrides[
        get_current_user_ws
    ] = override_get_current_user_ws

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(
            get_current_user_ws,
            None,
        )
