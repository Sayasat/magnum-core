from uuid import UUID

from app.core.security import hash_password
from app.modules.users.models import User
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserCreate
from app.shared.exceptions import ConflictException


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(self, data: UserCreate) -> User:
        existing_email = await self.repository.get_by_email(data.email)
        if existing_email:
            raise ConflictException("User with this email already exists")

        existing_username = await self.repository.get_by_username(data.username)

        if existing_username:
            raise ConflictException("User with this username already exists")

        user = await self.repository.create(
            email=data.email,
            username=data.username,
            hashed_password=hash_password(data.password),
        )

        return user

    async def list_users(self) -> list[User]:
        return await self.repository.list_users()

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.repository.get_by_email(email)

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        return await self.repository.get_by_id(user_id)