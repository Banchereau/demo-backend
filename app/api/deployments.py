from fastapi import APIRouter, Depends, HTTPException, status
from kubernetes.client.exceptions import ApiException

from app.core.security import get_current_user, require_role
from app.db.models.user import User, UserRole
from app.models.deployment import (
    Deployment,
    DeploymentScaleRequest,
    RolloutRevision,
)
from app.services.kubernetes import (
    get_deployment_rollouts,
    get_deployments,
    restart_deployment,
    scale_deployment,
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


@router.post(
    "/deployments/{namespace}/{name}/restart",
    status_code=status.HTTP_204_NO_CONTENT,
)
def deployment_restart(
    namespace: str,
    name: str,
    _: User = Depends(require_role(UserRole.OPERATOR)),
):
    try:
        restart_deployment(
            namespace=namespace,
            deployment_name=name,
        )
    except ApiException as e:
        raise HTTPException(
            status_code=e.status,
            detail=e.reason,
        )


@router.post(
    "/deployments/{namespace}/{name}/scale",
    status_code=status.HTTP_204_NO_CONTENT,
)
def deployment_scale(
    namespace: str,
    name: str,
    request: DeploymentScaleRequest,
    _: User = Depends(require_role(UserRole.OPERATOR)),
):
    try:
        scale_deployment(
            namespace=namespace,
            deployment_name=name,
            replicas=request.replicas,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except ApiException as e:
        raise HTTPException(
            status_code=e.status,
            detail=e.reason,
        )
