from fastapi import APIRouter, Depends, HTTPException
from kubernetes.client.exceptions import ApiException

from app.core.security import get_current_user
from app.models.deployment import Deployment, RolloutRevision
from app.services.kubernetes import (
    get_deployment_rollouts,
    get_deployments,
)

router = APIRouter(
    dependencies=[Depends(get_current_user)],
)

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

@router.get(
    "/deployments/{namespace}/{name}/rollouts",
    response_model=list[RolloutRevision],
)
def deployment_rollouts(
    namespace: str,
    name: str,
):
    try:
        return get_deployment_rollouts(
            namespace=namespace,
            deployment_name=name,
        )
    except ApiException as e:
        raise HTTPException(
            status_code=e.status,
            detail=e.reason,
        )
