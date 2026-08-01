from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["application"] == "demo-backend"
    assert data["status"] == "running"
    assert data["message"] == "Demo Backend running"
    assert data["version"] == "1.0.0"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_pods():
    mock_pods = [
        {
            "name": "demo-frontend-12345",
            "namespace": "default",
            "status": "Running",
            "restarts": 0,
            "node": "rpi",
            "age": "10m",
        }
    ]

    with patch(
        "app.api.pods.get_pods",
        return_value=mock_pods,
    ):
        response = client.get("/pods")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "demo-frontend-12345"
    assert data[0]["status"] == "Running"
