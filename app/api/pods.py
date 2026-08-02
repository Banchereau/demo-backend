from fastapi import APIRouter, HTTPException
from kubernetes.client.exceptions import ApiException

from app.models.pod import Pod
from app.services.kubernetes import get_pods

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
