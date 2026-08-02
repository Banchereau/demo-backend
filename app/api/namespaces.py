from fastapi import APIRouter

from app.services.kubernetes import get_namespaces
from app.models.namespace import KubernetesNamespace, NamespaceResponse


router = APIRouter()


@router.get("/namespaces", response_model=NamespaceResponse)
def namespaces():
    try:
        return {
            "status": "healthy",
            "namespaces": get_namespaces()
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "namespaces": [],
            "error": str(e)
        }
