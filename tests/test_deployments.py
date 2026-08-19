from unittest.mock import patch

from kubernetes.client.exceptions import ApiException

from app.core.config import settings
from app.services.kubernetes import scale_deployment


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


def test_restart_deployment_viewer_forbidden(
    authenticated_client,
):
    response = authenticated_client.post(
        "/deployments/default/demo-backend/restart"
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Insufficient permissions"
    }


def test_restart_deployment_operator(
    operator_client,
):
    with patch(
        "app.api.deployments.restart_deployment"
    ) as mock_restart:
        response = operator_client.post(
            "/deployments/default/demo-backend/restart"
        )

    assert response.status_code == 204

    mock_restart.assert_called_once_with(
        namespace="default",
        deployment_name="demo-backend",
    )


def test_restart_deployment_admin(
    admin_client,
):
    with patch(
        "app.api.deployments.restart_deployment"
    ) as mock_restart:
        response = admin_client.post(
            "/deployments/default/demo-backend/restart"
        )

    assert response.status_code == 204

    mock_restart.assert_called_once_with(
        namespace="default",
        deployment_name="demo-backend",
    )


def test_scale_deployment_viewer_forbidden(
    authenticated_client,
):
    response = authenticated_client.post(
        "/deployments/default/demo-backend/scale",
        json={"replicas": 2},
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Insufficient permissions"
    }


def test_scale_deployment_operator(
    operator_client,
):
    with patch(
        "app.api.deployments.scale_deployment"
    ) as mock_scale:
        response = operator_client.post(
            "/deployments/default/demo-backend/scale",
            json={"replicas": 3},
        )

    assert response.status_code == 204

    mock_scale.assert_called_once_with(
        namespace="default",
        deployment_name="demo-backend",
        replicas=3,
    )


def test_scale_deployment_admin(
    admin_client,
):
    with patch(
        "app.api.deployments.scale_deployment"
    ) as mock_scale:
        response = admin_client.post(
            "/deployments/default/demo-backend/scale",
            json={"replicas": 3},
        )

    assert response.status_code == 204

    mock_scale.assert_called_once_with(
        namespace="default",
        deployment_name="demo-backend",
        replicas=3,
    )


def test_scale_deployment_max_replicas(
    operator_client,
):
    with patch(
        "app.api.deployments.scale_deployment",
        side_effect=ValueError(
            "Maximum deployment replicas is 5"
        ),
    ) as mock_scale:
        response = operator_client.post(
            "/deployments/default/demo-backend/scale",
            json={"replicas": 6},
        )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Maximum deployment replicas is 5"
    }

    mock_scale.assert_called_once_with(
        namespace="default",
        deployment_name="demo-backend",
        replicas=6,
    )


def test_scale_deployment_negative_replicas(
    operator_client,
):
    response = operator_client.post(
        "/deployments/default/demo-backend/scale",
        json={"replicas": -1},
    )

    assert response.status_code == 422


def test_scale_deployment_service_rejects_above_max():
    with patch(
        "app.services.kubernetes.get_apps_v1"
    ) as mock_get_apps:
        try:
            scale_deployment(
                namespace="default",
                deployment_name="demo-backend",
                replicas=settings.max_deployment_replicas + 1,
            )
            assert False, "Expected ValueError"
        except ValueError as e:
            assert str(e) == (
                f"Maximum deployment replicas is "
                f"{settings.max_deployment_replicas}"
            )

        mock_get_apps.assert_not_called()
