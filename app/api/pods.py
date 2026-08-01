from fastapi import APIRouter

from app.models.pod import Pod
from app.services.kubernetes import get_pods


router = APIRouter()


@router.get("/pods", response_model=list[Pod])
def pods():
    return get_pods()
