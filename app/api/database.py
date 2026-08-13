from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user

router = APIRouter(
    prefix="/database",
    tags=["database"],
    dependencies=[Depends(get_current_user)],
)

@router.get("/health")
async def database_health(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("SELECT 1"))

    return {
        "status": "healthy",
        "database": result.scalar_one(),
    }
