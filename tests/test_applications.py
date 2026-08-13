from unittest.mock import patch


def test_get_applications(authenticated_client):
    mock_applications = [
        {
            "name": "demo-backend",
            "namespace": "default",
            "ingress": "demo-backend",
            "hosts": [
                "api.xcodewhisperer.fr"
            ],
            "service": "demo-backend",
            "deployment": "demo-backend",
            "desired_replicas": 1,
            "ready_replicas": 1,
            "pods": [
                "demo-backend-12345"
            ],
            "certificate": None,
            "status": "healthy",
        }
    ]

    with patch(
        "app.api.applications.get_applications",
        return_value=mock_applications,
    ):
        response = authenticated_client.get("/applications")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "demo-backend"
    assert data[0]["status"] == "healthy"


def test_demo_backend_application_exists(authenticated_client):
    mock_applications = [
        {
            "name": "demo-backend",
            "namespace": "default",
            "ingress": "demo-backend",
            "hosts": [
                "api.xcodewhisperer.fr"
            ],
            "service": "demo-backend",
            "deployment": "demo-backend",
            "desired_replicas": 1,
            "ready_replicas": 1,
            "pods": [
                "demo-backend-12345"
            ],
            "certificate": None,
            "status": "healthy",
        }
    ]

    with patch(
        "app.api.applications.get_applications",
        return_value=mock_applications,
    ):
        response = authenticated_client.get("/applications")

    applications = response.json()

    assert any(
        app["name"] == "demo-backend"
        for app in applications
    )


def test_application_structure(authenticated_client):
    mock_applications = [
        {
            "name": "demo-backend",
            "namespace": "default",
            "ingress": None,
            "hosts": [],
            "service": "demo-backend",
            "deployment": "demo-backend",
            "desired_replicas": 1,
            "ready_replicas": 1,
            "pods": [],
            "certificate": None,
            "status": "healthy",
        }
    ]

    with patch(
        "app.api.applications.get_applications",
        return_value=mock_applications,
    ):
        response = authenticated_client.get("/applications")

    app = response.json()[0]

    assert "name" in app
    assert "namespace" in app
    assert "status" in app
    assert "desired_replicas" in app
    assert "ready_replicas" in app

    assert app["desired_replicas"] == 1
    assert app["ready_replicas"] == 1
