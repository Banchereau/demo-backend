from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_applications():

    response = client.get("/applications")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_demo_backend_application_exists():

    response = client.get("/applications")

    assert response.status_code == 200

    applications = response.json()

    demo_backend = next(
        (
            application
            for application in applications
            if application["name"] == "demo-backend"
        ),
        None,
    )

    assert demo_backend is not None

    assert demo_backend["namespace"] == "default"

    assert demo_backend["service"] == "demo-backend"

    assert demo_backend["deployment"] == "demo-backend"


def test_application_structure():

    response = client.get("/applications")

    application = response.json()[0]

    assert "name" in application
    assert "namespace" in application
    assert "service" in application
    assert "deployment" in application
    assert "pods" in application
    assert "status" in application
