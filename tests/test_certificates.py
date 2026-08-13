from fastapi.testclient import TestClient

from app.main import app
from app.api import certificates


client = TestClient(app)


def test_certificates_endpoint(monkeypatch, authenticated_client):
    def mock_get_certificates(namespace=None):
        return [
            {
                "namespace": "default",
                "name": "demo-backend-tls",
                "secret_name": "demo-backend-tls",
                "dns_names": [
                    "api.xcodewhisperer.fr"
                ],
                "issuer": "letsencrypt-cloudflare",
                "ready": True,
                "status": "Certificate is up to date and has not expired",
                "not_after": "2026-10-26T12:11:23Z",
                "renewal_time": "2026-09-26T12:11:23Z",
            }
        ]

    monkeypatch.setattr(
        certificates,
        "get_certificates",
        mock_get_certificates
    )

    response = client.get("/certificates")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "demo-backend-tls"
    assert data[0]["ready"] is True


def test_certificates_namespace_filter(monkeypatch, authenticated_client):
    called = {}

    def mock_get_certificates(namespace=None):
        called["namespace"] = namespace

        return []

    monkeypatch.setattr(
        certificates,
        "get_certificates",
        mock_get_certificates
    )

    response = client.get(
        "/certificates?namespace=monitoring"
    )

    assert response.status_code == 200
    assert called["namespace"] == "monitoring"


def test_certificates_empty(monkeypatch, authenticated_client):
    def mock_get_certificates(namespace=None):
        return []

    monkeypatch.setattr(
        certificates,
        "get_certificates",
        mock_get_certificates
    )

    response = client.get("/certificates")

    assert response.status_code == 200
    assert response.json() == []
