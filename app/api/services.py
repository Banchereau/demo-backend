from fastapi import APIRouter, Depends, HTTPException
from kubernetes.client.exceptions import ApiException

from app.core.security import get_current_user
from app.models.service import Service
from app.services.kubernetes import get_services

router = APIRouter(
    dependencies=[Depends(get_current_user)],
)

@router.get("/services", response_model=list[Service])
def services():
    try:
        return get_services()
    except ApiException as e:
        raise HTTPException(
            status_code=e.status,
            detail=e.reason,
        )
