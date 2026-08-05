from fastapi import APIRouter

from app.models.health import PlatformHealth
from app.services.platform_health import get_platform_health


router = APIRouter(
    prefix="/health",
    tags=["health"]
)


@router.get(
    "/platform",
    response_model=PlatformHealth
)
def platform_health():

    return get_platform_health()
