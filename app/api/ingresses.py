from fastapi import APIRouter, Query

from app.services.ingresses import get_ingresses
from app.models.ingress import KubernetesIngress


router = APIRouter()


@router.get(
    "/ingresses",
    response_model=list[KubernetesIngress]
)
def list_ingresses(
    namespace: str | None = Query(default=None)
):

    return get_ingresses(namespace)
