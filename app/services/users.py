from app.core.security import hash_password, verify_password
from app.db.models.user import User, UserRole
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate


class UserAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class UserService:

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(
        self,
        data: UserCreate,
        force_password_change: bool = False,
    ) -> User:
        existing_username = await self.repository.get_by_username(
            data.username
        )

        if existing_username is not None:
            raise UserAlreadyExistsError("Username already exists")

        existing_email = await self.repository.get_by_email(
            data.email
        )

        if existing_email is not None:
            raise UserAlreadyExistsError("Email already exists")

        hashed_password = hash_password(data.password)

        return await self.repository.create(
            username=data.username,
            email=data.email,
            hashed_password=hashed_password,
            must_change_password=force_password_change,
            role=getattr(data, "role", UserRole.VIEWER),
        )


    async def authenticate_user(
        self,
        username: str,
        password: str,
    ) -> User:
        user = await self.repository.get_by_username(username)

        if user is None:
            raise InvalidCredentialsError()

        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InvalidCredentialsError()

        return user

    async def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str,
    ) -> User:
        if not verify_password(
            current_password,
            user.hashed_password,
        ):
            raise InvalidCredentialsError()

        user.hashed_password = hash_password(new_password)
        user.must_change_password = False

        await self.repository.db.commit()
        await self.repository.db.refresh(user)

        return user
