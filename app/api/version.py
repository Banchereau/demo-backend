from fastapi import APIRouter

from app.core import APP_NAME, APP_VERSION

router = APIRouter()


@router.get("/version")
def version():
    return {
        "application": APP_NAME,
        "version": APP_VERSION,
    }
