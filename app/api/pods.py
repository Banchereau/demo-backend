from fastapi import APIRouter, HTTPException
from kubernetes.client.exceptions import ApiException

from app.models.event import KubernetesEvent
from app.services.kubernetes import get_pod_events, get_pods
from app.models.pod import Pod

router = APIRouter()


@router.get("/pods", response_model=list[Pod])
def pods():
    try:
        return get_pods()
    except ApiException as e:
        raise HTTPException(
            status_code=e.status,
            detail=e.reason,
        )


@router.get(
    "/pods/{namespace}/{pod}/events",
    response_model=list[KubernetesEvent],
)
def pod_events(
    namespace: str,
    pod: str,
):
    try:
        return get_pod_events(
            namespace=namespace,
            pod=pod,
        )
    except ApiException as e:
        raise HTTPException(
            status_code=e.status,
            detail=e.reason,
        )
