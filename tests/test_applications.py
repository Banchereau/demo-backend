from unittest.mock import patch


def test_get_applications(client):

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
            "replicas": 1,
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
        response = client.get("/applications")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "demo-backend"
    assert data[0]["status"] == "healthy"


def test_demo_backend_application_exists(client):

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
            "replicas": 1,
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
        response = client.get("/applications")

    applications = response.json()

    assert any(
        app["name"] == "demo-backend"
        for app in applications
    )


def test_application_structure(client):

    mock_applications = [
        {
            "name": "demo-backend",
            "namespace": "default",
            "ingress": None,
            "hosts": [],
            "service": "demo-backend",
            "deployment": "demo-backend",
            "replicas": 1,
            "pods": [],
            "certificate": None,
            "status": "healthy",
        }
    ]

    with patch(
        "app.api.applications.get_applications",
        return_value=mock_applications,
    ):
        response = client.get("/applications")

    app = response.json()[0]

    assert "name" in app
    assert "namespace" in app
    assert "status" in app
    assert "replicas" in app
