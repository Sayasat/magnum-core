from fastapi import HTTPException, status
from app.core.security import create_access_token, verify_password
from app.modules.auth.schemas import RegisterRequest, AuthResponse, TokenResponse, LoginRequest
from app.modules.users.schemas import UserCreate, UserResponse
from app.modules.users.service import UserService
from app.modules.users.models import User


class AuthService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def register(self, data: RegisterRequest) -> AuthResponse:
        user = await self.user_service.create_user(
            UserCreate(
                email=data.email,
                username=data.username,
                password=data.password,
            )
        )
        token = self._create_token_for_user(user)
        return AuthResponse(
            user=UserResponse.model_validate(user),
            token=token,
        )

    async def login(self, data: LoginRequest) -> AuthResponse:
        user = await self.user_service.get_user_by_email(data.email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is inactive",
            )

        token = self._create_token_for_user(user)

        return AuthResponse(
            user=UserResponse.model_validate(user),
            token=token,
        )


    @staticmethod
    def _create_token_for_user(user: User) -> TokenResponse:
        access_token = create_access_token(
            subject=str(user.id),
            extra_claims={
                "email": user.email,
                "role": user.role.value,
            },
        )
        return TokenResponse(access_token=access_token)
