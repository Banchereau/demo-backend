from fastapi import APIRouter

from app.models.event import KubernetesEvent
from app.services.kubernetes import get_events


router = APIRouter(
    prefix="/events",
    tags=["events"],
)


@router.get(
    "",
    response_model=list[KubernetesEvent],
)
def list_events():
    return get_events()
