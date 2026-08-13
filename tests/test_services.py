from unittest.mock import patch

from kubernetes.client.exceptions import ApiException


def test_services(authenticated_client):
    mock_services = [
        {
            "name": "demo-backend",
            "namespace": "default",
            "type": "ClusterIP",
            "cluster_ip": "10.43.104.110",
            "ports": "80",
        }
    ]

    with patch(
        "app.api.services.get_services",
        return_value=mock_services,
    ):
        response = authenticated_client.get("/services")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "demo-backend"
    assert data[0]["type"] == "ClusterIP"


def test_services_kubernetes_error(authenticated_client):
    with patch(
        "app.api.services.get_services",
        side_effect=ApiException(
            status=403,
            reason="Forbidden",
        ),
    ):
        response = authenticated_client.get("/services")

    assert response.status_code == 403

    data = response.json()

    assert data["detail"] == "Forbidden"
