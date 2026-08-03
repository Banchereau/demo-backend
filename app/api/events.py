from fastapi import APIRouter, Query

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
def list_events(
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
    namespace: str | None = None,
    type: str | None = None,
):
    return get_events(
        limit=limit,
        namespace=namespace,
        event_type=type,
    )
