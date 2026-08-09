from kubernetes.stream import stream

from app.core.kubernetes import get_core_v1


def connect_pod_exec(
    namespace: str,
    pod_name: str,
    container: str | None = None,
):
    api = get_core_v1()

    command = [
        "/bin/bash"
    ]

    kwargs = {
        "name": pod_name,
        "namespace": namespace,
        "command": command,
        "stderr": True,
        "stdin": True,
        "stdout": True,
        "tty": True,
        "_preload_content": False,
    }

    if container:
        kwargs["container"] = container

    return stream(
        api.connect_get_namespaced_pod_exec,
        **kwargs,
    )
