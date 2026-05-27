from app.modules.users.repository import UserRepository
from app.shared.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import create_access_token, verify_password
from app.modules.auth.schemas import RegisterRequest, AuthResponse, TokenResponse, LoginRequest
from app.modules.users.schemas import UserCreate, UserResponse
from app.modules.users.service import UserService
from app.modules.users.models import User
from app.modules.users.repository import UserRepository


class AuthService:
    def __init__(self, user_service: UserService, user_repository: UserRepository):
        self.user_service = user_service
        self.user_repository = user_repository


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
        user = await self.user_repository.get_by_email(data.email)

        if not user:
            raise UnauthorizedException("Invalid email or password")

        if not verify_password(data.password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise ForbiddenException("User is inactive")

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
