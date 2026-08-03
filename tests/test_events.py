from fastapi.testclient import TestClient

from app.main import app
from app.api import events


client = TestClient(app)


def fake_events():
    return [
        {
            "namespace": "default",
            "name": "demo-backend.test",
            "type": "Normal",
            "reason": "Started",
            "message": "Container started",
            "involved_object": "Pod/demo-backend",
            "timestamp": "2026-08-03T10:00:00Z",
        }
    ]


def test_events_endpoint(monkeypatch):
    monkeypatch.setattr(
        events,
        "get_events",
        fake_events,
    )

    response = client.get("/events")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert data[0]["namespace"] == "default"
    assert data[0]["type"] == "Normal"
