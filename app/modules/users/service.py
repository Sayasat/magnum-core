from fastapi import HTTPException, status

from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserCreate
from app.modules.users.models import User


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(self, data: UserCreate) -> User:
        existing_email = await self.repository.get_by_email(data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

        existing_username = await self.repository.get_by_username(data.username)

        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this username already exists",
            )

        user = await self.repository.create(
            email=data.email,
            username=data.username,
            hashed_password=data.password,
        )

        return user

    async def list_users(self) -> list[User]:
        return await self.repository.list_users()