from fastapi.testclient import TestClient

from app.main import app
from app.api import ingresses


client = TestClient(app)


def test_ingresses_endpoint(monkeypatch, authenticated_client):
    def mock_get_ingresses(namespace=None):
        return [
            {
                "namespace": "default",
                "name": "demo-backend",
                "hosts": [
                    "api.xcodewhisperer.fr"
                ],
                "service": "demo-backend",
                "tls_secret": "demo-backend-tls",
            }
        ]

    monkeypatch.setattr(
        ingresses,
        "get_ingresses",
        mock_get_ingresses
    )

    response = client.get("/ingresses")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "demo-backend"
    assert data[0]["hosts"][0] == "api.xcodewhisperer.fr"
    assert data[0]["tls_secret"] == "demo-backend-tls"


def test_ingresses_namespace_filter(monkeypatch, authenticated_client):
    called = {}

    def mock_get_ingresses(namespace=None):
        called["namespace"] = namespace

        return []

    monkeypatch.setattr(
        ingresses,
        "get_ingresses",
        mock_get_ingresses
    )

    response = client.get(
        "/ingresses?namespace=monitoring"
    )

    assert response.status_code == 200
    assert called["namespace"] == "monitoring"


def test_ingresses_empty(monkeypatch, authenticated_client):
    def mock_get_ingresses(namespace=None):
        return []

    monkeypatch.setattr(
        ingresses,
        "get_ingresses",
        mock_get_ingresses
    )

    response = client.get("/ingresses")

    assert response.status_code == 200
    assert response.json() == []
