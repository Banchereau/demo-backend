from fastapi import APIRouter, Depends, Query

from app.core.security import get_current_user
from app.services.ingresses import get_ingresses
from app.models.ingress import KubernetesIngress

router = APIRouter(
    dependencies=[Depends(get_current_user)],
)

@router.get(
    "/ingresses",
    response_model=list[KubernetesIngress],
)
def list_ingresses(
    namespace: str | None = Query(default=None),
):
    return get_ingresses(namespace)
