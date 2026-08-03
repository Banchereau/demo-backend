from fastapi import APIRouter, Query

from app.services.certificates import get_certificates
from app.models.certificate import Certificate


router = APIRouter(
    prefix="/certificates",
    tags=["certificates"],
)


@router.get("", response_model=list[Certificate])
def certificates(
    namespace: str | None = Query(default=None)
):
    return get_certificates(namespace)
