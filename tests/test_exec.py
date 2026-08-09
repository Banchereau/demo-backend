from unittest.mock import MagicMock, patch

import pytest
from kubernetes.client.exceptions import ApiException, NotFoundException
from app.services.pod_exec import connect_pod_exec


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
