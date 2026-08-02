from unittest.mock import patch

from kubernetes.client.exceptions import ApiException


def test_deployments(client):

    mock_deployments = [
        {
            "name": "demo-backend",
            "namespace": "default",
            "replicas": 1,
            "ready_replicas": 1,
            "available_replicas": 1,
            "strategy": "RollingUpdate",
            "images": "ghcr.io/banchereau/demo-backend:latest",
        }
    ]

    with patch(
        "app.api.deployments.get_deployments",
        return_value=mock_deployments,
    ):
        response = client.get("/deployments")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert data[0]["name"] == "demo-backend"
    assert data[0]["namespace"] == "default"
    assert data[0]["replicas"] == 1
    assert data[0]["ready_replicas"] == 1
    assert data[0]["available_replicas"] == 1
    assert data[0]["strategy"] == "RollingUpdate"
    assert (
        data[0]["images"]
        == "ghcr.io/banchereau/demo-backend:latest"
    )


def test_deployments_kubernetes_error(client):

    with patch(
        "app.api.deployments.get_deployments",
        side_effect=ApiException(
            status=403,
            reason="Forbidden",
        ),
    ):
        response = client.get("/deployments")

    assert response.status_code == 403

    assert response.json() == {
        "detail": "Forbidden"
    }
