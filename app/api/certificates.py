from fastapi import APIRouter, Depends, Query

from app.core.security import get_current_user
from app.services.certificates import get_certificates
from app.models.certificate import Certificate

router = APIRouter(
    prefix="/certificates",
    tags=["certificates"],
    dependencies=[Depends(get_current_user)],
)

@router.get("", response_model=list[Certificate])
def certificates(
    namespace: str | None = Query(default=None),
):
    return get_certificates(namespace)
