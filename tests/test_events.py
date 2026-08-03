from app.main import app
from fastapi.testclient import TestClient

from app.api import events


client = TestClient(app)


def fake_events(
    limit=50,
    namespace=None,
    event_type=None,
):
    return [
        {
            "namespace": "default",
            "name": "test-event",
            "type": "Normal",
            "reason": "Created",
            "message": "Pod created",
            "involved_object": "Pod/test",
            "timestamp": "2026-08-03T10:00:00+00:00",
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
    assert len(response.json()) == 1


def test_events_limit_parameter(monkeypatch):
    called = {}

    def fake_events(
        limit=50,
        namespace=None,
        event_type=None,
    ):
        called["limit"] = limit
        return []

    monkeypatch.setattr(
        events,
        "get_events",
        fake_events,
    )

    response = client.get("/events?limit=10")

    assert response.status_code == 200
    assert called["limit"] == 10

def test_events_namespace_filter(monkeypatch):
    called = {}

    def fake_events(
        limit=50,
        namespace=None,
        event_type=None,
    ):
        called["namespace"] = namespace
        return []

    monkeypatch.setattr(
        events,
        "get_events",
        fake_events,
    )

    response = client.get(
        "/events?namespace=default"
    )

    assert response.status_code == 200
    assert called["namespace"] == "default"


def test_events_type_filter(monkeypatch):
    called = {}

    def fake_events(
        limit=50,
        namespace=None,
        event_type=None,
    ):
        called["event_type"] = event_type
        return []

    monkeypatch.setattr(
        events,
        "get_events",
        fake_events,
    )

    response = client.get(
        "/events?type=Warning"
    )

    assert response.status_code == 200
    assert called["event_type"] == "Warning"


def test_events_invalid_limit():
    response = client.get(
        "/events?limit=0"
    )

    assert response.status_code == 422


def test_events_limit_maximum():
    response = client.get(
        "/events?limit=201"
    )

    assert response.status_code == 422
