from fastapi import APIRouter, HTTPException

from app.services.logs import get_pod_logs


router = APIRouter()


@router.get("/pods/{namespace}/{pod}/logs")
def pod_logs(
    namespace: str,
    pod: str,
    tail: int = 200,
    timestamps: bool = False,
    previous: bool = False,
    container: str | None = None,
):
    try:
        return get_pod_logs(
            namespace=namespace,
            pod=pod,
            tail_lines=tail,
            timestamps=timestamps,
            previous=previous,
            container=container,
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
