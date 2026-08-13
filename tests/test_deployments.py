from unittest.mock import patch

from kubernetes.client.exceptions import ApiException


def test_deployments(authenticated_client):
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
        response = authenticated_client.get("/deployments")

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


def test_deployments_kubernetes_error(authenticated_client):
    with patch(
        "app.api.deployments.get_deployments",
        side_effect=ApiException(
            status=403,
            reason="Forbidden",
        ),
    ):
        response = authenticated_client.get("/deployments")

    assert response.status_code == 403

    assert response.json() == {
        "detail": "Forbidden"
    }


def test_deployment_rollouts(authenticated_client):
    mock_rollouts = [
        {
            "revision": 5,
            "replicas": 1,
            "ready_replicas": 1,
            "image": "ghcr.io/banchereau/demo-backend:latest",
            "created_at": "2026-08-09T20:15:00+00:00",
            "is_current": True,
        },
        {
            "revision": 4,
            "replicas": 1,
            "ready_replicas": 1,
            "image": "ghcr.io/banchereau/demo-backend:v1.2.0",
            "created_at": "2026-08-08T18:30:00+00:00",
            "is_current": False,
        },
    ]

    with patch(
        "app.api.deployments.get_deployment_rollouts",
        return_value=mock_rollouts,
    ):
        response = authenticated_client.get(
            "/deployments/default/demo-backend/rollouts"
        )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    assert data[0]["revision"] == 5
    assert data[0]["replicas"] == 1
    assert data[0]["ready_replicas"] == 1
    assert (
        data[0]["image"]
        == "ghcr.io/banchereau/demo-backend:latest"
    )
    assert data[0]["is_current"] is True

    assert data[1]["revision"] == 4
    assert data[1]["is_current"] is False


def test_deployment_rollouts_kubernetes_error(authenticated_client):
    with patch(
        "app.api.deployments.get_deployment_rollouts",
        side_effect=ApiException(
            status=403,
            reason="Forbidden",
        ),
    ):
        response = authenticated_client.get(
            "/deployments/default/demo-backend/rollouts"
        )

    assert response.status_code == 403

    assert response.json() == {
        "detail": "Forbidden"
    }
