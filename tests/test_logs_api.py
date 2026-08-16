from unittest.mock import MagicMock, patch

import pytest
from fastapi import WebSocketDisconnect

from kubernetes.client.exceptions import ApiException


def test_pod_logs_endpoint(monkeypatch, authenticated_client):
    class MockCoreApi:
        def read_namespaced_pod_log(
            self,
            name,
            namespace,
            **kwargs,
        ):
            assert name == "demo-backend-12345"
            assert namespace == "default"

            assert kwargs["tail_lines"] == 200
            assert kwargs["timestamps"] is False
            assert kwargs["previous"] is False
            assert kwargs["container"] is None

            return (
                "INFO Application started\n"
                "INFO Connected database\n"
                "INFO Listening on port 8000\n"
            )

    monkeypatch.setattr(
        "app.services.logs.get_core_v1",
        lambda: MockCoreApi(),
    )

    response = authenticated_client.get(
        "/pods/default/demo-backend-12345/logs"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["namespace"] == "default"
    assert data["pod"] == "demo-backend-12345"

    assert "Application started" in data["logs"]
    assert "Listening on port 8000" in data["logs"]


def test_pod_logs_endpoint_with_parameters(
    monkeypatch,
    authenticated_client,
):
    class MockCoreApi:
        def read_namespaced_pod_log(
            self,
            name,
            namespace,
            **kwargs,
        ):
            assert name == "demo-backend-12345"
            assert namespace == "default"

            assert kwargs["tail_lines"] == 50
            assert kwargs["timestamps"] is True
            assert kwargs["previous"] is True
            assert kwargs["container"] == "backend"

            return "previous container logs"

    monkeypatch.setattr(
        "app.services.logs.get_core_v1",
        lambda: MockCoreApi(),
    )

    response = authenticated_client.get(
        "/pods/default/demo-backend-12345/logs"
        "?tail=50"
        "&timestamps=true"
        "&previous=true"
        "&container=backend"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["logs"] == "previous container logs"


def test_pod_logs_kubernetes_error(
    monkeypatch,
    authenticated_client,
):
    class MockCoreApi:
        def read_namespaced_pod_log(
            self,
            *args,
            **kwargs,
        ):
            raise Exception("Kubernetes unavailable")

    monkeypatch.setattr(
        "app.services.logs.get_core_v1",
        lambda: MockCoreApi(),
    )

    response = authenticated_client.get(
        "/pods/default/demo-backend-12345/logs"
    )

    assert response.status_code == 500


def test_pod_logs_not_found(
    authenticated_client,
    monkeypatch,
):
    class MockCoreApi:
        def read_namespaced_pod_log(
            self,
            *args,
            **kwargs,
        ):
            raise ApiException(
                status=404,
                reason="Not Found",
            )

    monkeypatch.setattr(
        "app.services.logs.get_core_v1",
        lambda: MockCoreApi(),
    )

    response = authenticated_client.get(
        "/pods/default/does-not-exist/logs"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Pod not found"


def test_pod_logs_websocket_requires_authentication(client):
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(
            "/logs/default/demo-backend-12345"
        ):
            pass


def test_pod_logs_websocket_unauthenticated_does_not_reach_kubernetes(
    client,
):
    with patch(
        "app.api.logs.stream_pod_logs"
    ) as mock_stream:
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect(
                "/logs/default/demo-backend-12345"
            ):
                pass

        mock_stream.assert_not_called()


def test_pod_logs_websocket_authenticated(
    authenticated_ws_client,
):
    response = MagicMock()

    response.stream.return_value = iter(
        [
            b"INFO Application started\n",
            b"INFO Listening on port 8000\n",
        ]
    )

    with patch(
        "app.api.logs.stream_pod_logs",
        return_value=response,
    ) as mock_stream:
        with authenticated_ws_client.websocket_connect(
            "/logs/default/demo-backend-12345"
        ) as websocket:
            first = websocket.receive_text()
            second = websocket.receive_text()

        assert first == "INFO Application started\n"
        assert second == "INFO Listening on port 8000\n"

        mock_stream.assert_called_once_with(
            namespace="default",
            pod="demo-backend-12345",
            tail_lines=20,
            timestamps=False,
            previous=False,
            container=None,
        )

        response.close.assert_called_once()
