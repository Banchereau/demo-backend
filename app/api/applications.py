from fastapi import APIRouter

from app.models.application import KubernetesApplication
from app.services.applications import get_applications


router = APIRouter(
    prefix="/applications",
    tags=["applications"]
)


@router.get(
    "",
    response_model=list[KubernetesApplication]
)
def read_applications():
    return get_applications()
