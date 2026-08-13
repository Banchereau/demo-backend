from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app


client = TestClient(app)


def test_get_namespaces(
    authenticated_client,
):
    mock_namespaces = [
        {
            "name": "default",
            "status": "Active",
        },
        {
            "name": "monitoring",
            "status": "Active",
        },
    ]

    with patch(
        "app.api.namespaces.get_namespaces",
        return_value=mock_namespaces,
    ):
        response = authenticated_client.get(
            "/namespaces"
        )

    assert response.status_code == 200

    data = response.json()

    assert len(data["namespaces"]) == 2

    assert data["namespaces"][0]["name"] == "default"
    assert data["namespaces"][0]["status"] == "Active"


def test_get_namespaces_structure(
    authenticated_client,
):
    mock_namespaces = [
        {
            "name": "kube-system",
            "status": "Active",
        }
    ]

    with patch(
        "app.api.namespaces.get_namespaces",
        return_value=mock_namespaces,
    ):
        response = authenticated_client.get(
            "/namespaces"
        )

    assert response.status_code == 200

    data = response.json()

    namespace = data["namespaces"][0]

    assert "name" in namespace
    assert "status" in namespace


def test_get_namespaces_error(
    authenticated_client,
):
    with patch(
        "app.api.namespaces.get_namespaces",
        side_effect=Exception(
            "Kubernetes API unavailable"
        ),
    ):
        response = authenticated_client.get(
            "/namespaces"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "unhealthy"
    assert data["namespaces"] == []
    assert (
        "Kubernetes API unavailable"
        in data["error"]
    )
