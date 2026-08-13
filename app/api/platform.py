from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.models.health import PlatformHealth
from app.services.platform_health import get_platform_health

router = APIRouter(
    prefix="/health",
    tags=["health"],
    dependencies=[Depends(get_current_user)],
)

@router.get(
    "/platform",
    response_model=PlatformHealth,
)
def platform_health():
    return get_platform_health()
