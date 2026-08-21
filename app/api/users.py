from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_role
from app.db.models.user import User, UserRole
from app.repositories.user import UserRepository
from app.schemas.user import AdminUserCreate, UserResponse
from app.services.users import UserAlreadyExistsError, UserService


router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "",
    response_model=list[UserResponse],
)
async def list_users(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.ADMIN)),
):
    repository = UserRepository(db)
    return await repository.get_all()


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    data: AdminUserCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.ADMIN)),
):
    repository = UserRepository(db)
    service = UserService(repository)

    try:
        user = await service.create_user(
            data,
            force_password_change=True,
        )

        user.role = data.role
        return user

    except UserAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
