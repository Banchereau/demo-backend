from fastapi import APIRouter, HTTPException
from kubernetes.client.exceptions import ApiException

from app.models.deployment import Deployment
from app.services.kubernetes import get_deployments


router = APIRouter()


@router.get(
    "/deployments",
    response_model=list[Deployment],
)
def deployments():
    try:
        return get_deployments()

    except ApiException as e:
        raise HTTPException(
            status_code=e.status,
            detail=e.reason,
        )
