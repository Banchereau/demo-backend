from fastapi import APIRouter
from typing import Union

from app.models.cluster import ClusterStatus, ClusterError
from app.services.kubernetes import get_cluster_status


router = APIRouter()


@router.get(
    "/cluster",
    response_model=Union[ClusterStatus, ClusterError]
)
def cluster():
    return get_cluster_status()
