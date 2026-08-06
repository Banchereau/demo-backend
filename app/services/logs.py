from kubernetes import client
from kubernetes.client.exceptions import ApiException
from fastapi import HTTPException

from app.core.kubernetes import get_core_v1
from app.models.logs import PodLogs


def get_pod_logs(
    namespace: str,
    pod: str,
    tail_lines: int = 200,
    timestamps: bool = False,
    previous: bool = False,
    container: str | None = None,
) -> PodLogs:

    core_v1: client.CoreV1Api = get_core_v1()

    try:
        logs = core_v1.read_namespaced_pod_log(
            name=pod,
            namespace=namespace,
            tail_lines=tail_lines,
            timestamps=timestamps,
            previous=previous,
            container=container,
        )

        if isinstance(logs, bytes):
            logs = logs.decode("utf-8")

        elif isinstance(logs, str) and logs.startswith("b'"):
            logs = logs[2:-1].encode().decode("unicode_escape")

        return PodLogs(
            namespace=namespace,
            pod=pod,
            logs=logs,
        )

    except ApiException as e:
        if e.status == 404:
            raise HTTPException(
                status_code=404,
                detail="Pod not found",
            )

        raise
