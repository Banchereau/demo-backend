from fastapi import APIRouter, Depends
from typing import Union

from app.core.security import get_current_user
from app.models.cluster import ClusterStatus, ClusterError
from app.services.kubernetes import get_cluster_status

router = APIRouter(
    dependencies=[Depends(get_current_user)],
)

@router.get(
    "/cluster",
    response_model=Union[ClusterStatus, ClusterError],
)
def cluster():
    return get_cluster_status()
