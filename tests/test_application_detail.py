from unittest.mock import patch


def test_application_detail(authenticated_client):
    mock_application_detail = {
        "name": "demo-backend",
        "namespace": "default",
        "status": "healthy",
        "deployment": {
            "name": "demo-backend",
            "desired_replicas": 1,
            "ready_replicas": 1,
            "image": "ghcr.io/banchereau/demo-backend:latest",
        },
        "service": {
            "name": "demo-backend",
            "type": "ClusterIP",
            "cluster_ip": "10.43.0.10",
        },
        "ingress": {
            "name": "demo-backend",
            "hosts": [
                "api.xcodewhisperer.fr"
            ],
            "tls": True,
        },
        "pods": [
            {
                "name": "demo-backend-12345",
                "status": "Running",
                "restarts": 0,
            }
        ],
        "certificates": [],
    }

    with patch(
        "app.api.applications.get_application_detail",
        return_value=mock_application_detail,
    ):
        response = authenticated_client.get(
            "/applications/default/demo-backend"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "demo-backend"
    assert data["namespace"] == "default"
    assert data["status"] == "healthy"

    assert data["deployment"]["name"] == "demo-backend"
    assert data["deployment"]["ready_replicas"] == 1

    assert data["service"]["name"] == "demo-backend"

    assert data["ingress"]["hosts"] == [
        "api.xcodewhisperer.fr"
    ]

    assert len(data["pods"]) == 1
    assert data["pods"][0]["status"] == "Running"
