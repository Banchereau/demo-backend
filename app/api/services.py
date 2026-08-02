from fastapi import APIRouter, HTTPException
from kubernetes.client.exceptions import ApiException

from app.models.service import Service
from app.services.kubernetes import get_services


router = APIRouter()


@router.get("/services", response_model=list[Service])
def services():
    try:
        return get_services()

    except ApiException as e:
        raise HTTPException(
            status_code=e.status,
            detail=e.reason,
        )
