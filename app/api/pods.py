from fastapi import APIRouter, Depends, HTTPException
from kubernetes.client.exceptions import ApiException

from app.core.security import get_current_user
from app.models.event import KubernetesEvent
from app.models.pod import (
    Pod,
    PodDetail,
    PodRestart,
)
from app.services.kubernetes import (
    get_pod_detail,
    get_pod_events,
    get_pod_restarts,
    get_pods,
)

router = APIRouter(
    dependencies=[Depends(get_current_user)],
)


@router.get(
    "/pods",
    response_model=list[Pod],
)
def pods():
    try:
        return get_pods()
    except ApiException as e:
        raise HTTPException(
            status_code=e.status,
            detail=e.reason,
        )


@router.get(
    "/pods/{namespace}/{pod}",
    response_model=PodDetail,
)
def pod_detail(
    namespace: str,
    pod: str,
):
    try:
        return get_pod_detail(
            namespace=namespace,
            pod=pod,
        )
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


@router.get(
    "/pods/{namespace}/{pod}/restarts",
    response_model=list[PodRestart],
)
def pod_restarts(
    namespace: str,
    pod: str,
):
    try:
        return get_pod_restarts(
            namespace=namespace,
            pod=pod,
        )
    except ApiException as e:
        raise HTTPException(
            status_code=e.status,
            detail=e.reason,
        )
