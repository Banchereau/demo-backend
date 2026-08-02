from unittest.mock import patch

from kubernetes.client.exceptions import ApiException


def test_pods(client):
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


def test_pods_kubernetes_error(client):
    with patch(
        "app.api.pods.get_pods",
        side_effect=ApiException(
            status=403,
            reason="Forbidden",
        ),
    ):
        response = client.get("/pods")

    assert response.status_code == 403

    data = response.json()

    assert data["detail"] == "Forbidden"
