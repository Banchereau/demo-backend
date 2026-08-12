from app.core.security import hash_password, verify_password
from app.db.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate


class UserAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class UserService:

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(self, data: UserCreate) -> User:
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
