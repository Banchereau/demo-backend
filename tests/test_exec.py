from unittest.mock import MagicMock, patch

import pytest
from kubernetes.client.exceptions import ApiException, NotFoundException
from app.services.pod_exec import connect_pod_exec
from fastapi import WebSocketDisconnect

def test_connect_pod_exec_pod_not_found():
    api = MagicMock()

    api.read_namespaced_pod.side_effect = NotFoundException(
        status=404,
        reason="Not Found",
    )

    with patch(
        "app.services.pod_exec.get_core_v1",
        return_value=api,
    ):
        with pytest.raises(NotFoundException) as exc_info:
            connect_pod_exec(
                "default",
                "missing-pod",
            )

    assert exc_info.value.status == 404
    api.read_namespaced_pod.assert_called_once_with(
        name="missing-pod",
        namespace="default",
    )


def test_connect_pod_exec_container_not_found():
    api = MagicMock()

    pod = MagicMock()
    pod.spec.containers = [
        MagicMock(name="backend"),
    ]

    api.read_namespaced_pod.return_value = pod

    with patch(
        "app.services.pod_exec.get_core_v1",
        return_value=api,
    ):
        with pytest.raises(Exception) as exc_info:
            connect_pod_exec(
                "default",
                "demo-pod",
                container="missing-container",
            )

    assert "missing-container" in str(exc_info.value)


def test_connect_pod_exec_uses_bash_and_tty():
    api = MagicMock()

    pod = MagicMock()

    container = MagicMock()
    container.name = "backend"

    pod.spec.containers = [
        container,
    ]

    api.read_namespaced_pod.return_value = pod

    fake_shell = MagicMock()

    with patch(
        "app.services.pod_exec.get_core_v1",
        return_value=api,
    ), patch(
        "app.services.pod_exec.stream",
        return_value=fake_shell,
    ) as mock_stream:
        result = connect_pod_exec(
            "default",
            "demo-pod",
            container="backend",
        )

    assert result is fake_shell

    mock_stream.assert_called_once()

    kwargs = mock_stream.call_args.kwargs

    assert kwargs["command"] == ["/bin/bash"]
    assert kwargs["stdin"] is True
    assert kwargs["stdout"] is True
    assert kwargs["stderr"] is True
    assert kwargs["tty"] is True
    assert kwargs["_preload_content"] is False
    assert kwargs["container"] == "backend"


def test_connect_pod_exec_forbidden():
    api = MagicMock()

    with patch(
        "app.services.pod_exec.get_core_v1",
        return_value=api,
    ):
        api.read_namespaced_pod.side_effect = ApiException(
            status=403,
            reason="Forbidden",
        )

        with pytest.raises(ApiException) as exc:
            connect_pod_exec(
                "default",
                "demo-pod",
            )

    assert exc.value.status == 403


def test_exec_websocket_requires_authentication(client):
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(
            "/exec/default/demo-pod"
        ):
            pass


def test_exec_websocket_authenticated(
    authenticated_ws_client,
):
    with patch(
        "app.api.exec.connect_pod_exec"
    ) as mock_connect:
        shell = MagicMock()
        shell.is_open.return_value = False
        mock_connect.return_value = shell

        with authenticated_ws_client.websocket_connect(
            "/exec/default/demo-pod"
        ) as websocket:
            message = websocket.receive_text()

        assert message == "Connected to pod shell\r\n"
        mock_connect.assert_called_once_with(
            "default",
            "demo-pod",
        )


def test_exec_websocket_unauthenticated_does_not_reach_kubernetes(
    client,
):
    with patch(
        "app.api.exec.connect_pod_exec"
    ) as mock_connect:
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect(
                "/exec/default/demo-pod"
            ):
                pass

        mock_connect.assert_not_called()
