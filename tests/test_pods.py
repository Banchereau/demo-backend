from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

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


def test_pod_events(client):
    mock_events = [
        {
            "namespace": "default",
            "name": "demo-backend-event",
            "type": "Warning",
            "reason": "Unhealthy",
            "message": "Readiness probe failed",
            "involved_object": "Pod/demo-backend-12345",
            "timestamp": "2026-08-09T10:00:00+00:00",
        }
    ]

    with patch(
        "app.api.pods.get_pod_events",
        return_value=mock_events,
    ):
        response = client.get(
            "/pods/default/demo-backend-12345/events"
        )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["type"] == "Warning"
    assert data[0]["reason"] == "Unhealthy"
    assert data[0]["involved_object"] == "Pod/demo-backend-12345"


def test_pod_events_kubernetes_error(client):
    with patch(
        "app.api.pods.get_pod_events",
        side_effect=ApiException(
            status=403,
            reason="Forbidden",
        ),
    ):
        response = client.get(
            "/pods/default/demo-backend-12345/events"
        )

    assert response.status_code == 403

    data = response.json()

    assert data["detail"] == "Forbidden"


def test_get_pod_events_filters_by_pod():
    target_event = MagicMock()
    target_event.metadata.namespace = "default"
    target_event.metadata.name = "event-target"
    target_event.type = "Warning"
    target_event.reason = "Unhealthy"
    target_event.message = "Readiness probe failed"
    target_event.involved_object.kind = "Pod"
    target_event.involved_object.name = "demo-backend-12345"
    target_event.last_timestamp = datetime(
        2026,
        8,
        9,
        10,
        0,
        tzinfo=timezone.utc,
    )
    target_event.event_time = None
    target_event.first_timestamp = None

    other_pod_event = MagicMock()
    other_pod_event.metadata.namespace = "default"
    other_pod_event.metadata.name = "event-other"
    other_pod_event.type = "Normal"
    other_pod_event.reason = "Started"
    other_pod_event.message = "Started container"
    other_pod_event.involved_object.kind = "Pod"
    other_pod_event.involved_object.name = "other-pod"
    other_pod_event.last_timestamp = datetime(
        2026,
        8,
        9,
        9,
        0,
        tzinfo=timezone.utc,
    )
    other_pod_event.event_time = None
    other_pod_event.first_timestamp = None

    deployment_event = MagicMock()
    deployment_event.metadata.namespace = "default"
    deployment_event.metadata.name = "event-deployment"
    deployment_event.type = "Normal"
    deployment_event.reason = "ScalingReplicaSet"
    deployment_event.message = "Scaled up replica set"
    deployment_event.involved_object.kind = "Deployment"
    deployment_event.involved_object.name = "demo-backend"
    deployment_event.last_timestamp = datetime(
        2026,
        8,
        9,
        8,
        0,
        tzinfo=timezone.utc,
    )
    deployment_event.event_time = None
    deployment_event.first_timestamp = None

    mock_api = MagicMock()
    mock_api.list_namespaced_event.return_value.items = [
        other_pod_event,
        deployment_event,
        target_event,
    ]

    with patch(
        "app.services.kubernetes.get_core_v1",
        return_value=mock_api,
    ):
        from app.services.kubernetes import get_pod_events

        result = get_pod_events(
            namespace="default",
            pod="demo-backend-12345",
        )

    assert len(result) == 1
    assert result[0]["name"] == "event-target"
    assert result[0]["involved_object"] == "Pod/demo-backend-12345"
    assert result[0]["reason"] == "Unhealthy"


def test_pod_detail(client):
    mock_pod = {
        "name": "demo-backend-12345",
        "namespace": "default",
        "status": "Running",
        "restarts": 2,
        "node": "rpi",
        "age": "10m",
        "pod_ip": "10.42.0.15",
        "host_ip": "192.168.1.93",
        "service_account": "default",
        "containers": ["demo-backend"],
        "images": ["ghcr.io/banchereau/demo-backend:latest"],
    }

    with patch(
        "app.api.pods.get_pod_detail",
        return_value=mock_pod,
    ):
        response = client.get(
            "/pods/default/demo-backend-12345"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "demo-backend-12345"
    assert data["namespace"] == "default"
    assert data["status"] == "Running"
    assert data["restarts"] == 2
    assert data["node"] == "rpi"
    assert data["pod_ip"] == "10.42.0.15"
    assert data["containers"] == ["demo-backend"]


def test_pod_detail_kubernetes_error(client):
    with patch(
        "app.api.pods.get_pod_detail",
        side_effect=ApiException(
            status=404,
            reason="Not Found",
        ),
    ):
        response = client.get(
            "/pods/default/unknown-pod"
        )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Not Found"
