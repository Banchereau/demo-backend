from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.models.application import (
    KubernetesApplication,
    ApplicationDetail,
)
from app.services.applications import (
    get_applications,
    get_application_detail,
)

router = APIRouter(
    prefix="/applications",
    tags=["applications"],
    dependencies=[Depends(get_current_user)],
)

@router.get(
    "",
    response_model=list[KubernetesApplication],
)
def read_applications():
    return get_applications()

@router.get(
    "/{namespace}/{name}",
    response_model=ApplicationDetail,
)
def read_application_detail(
    namespace: str,
    name: str,
):
    return get_application_detail(
        namespace,
        name,
    )
