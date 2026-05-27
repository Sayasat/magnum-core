from fastapi import Depends
from app.shared.exceptions import ForbiddenException, UnauthorizedException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from uuid import UUID

from app.core.security import decode_access_token
from app.modules.auth.service import AuthService
from app.modules.users.dependencies import get_user_service
from app.modules.users.service import UserService
from app.modules.users.models import User
from app.modules.users.enums import UserRole


def get_auth_service(
    user_service: UserService = Depends(get_user_service),
) -> AuthService:
    return AuthService(user_service=user_service)

bearer_scheme = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    user_service: UserService = Depends(get_user_service),) -> User:
    token = credentials.credentials

    try:
        payload = decode_access_token(token)
        user_id_raw = payload.get("sub")

        if user_id_raw is None:
            raise UnauthorizedException("Invalid authentication token")

        user_id = UUID(user_id_raw)

    except (JWTError, ValueError):
        raise UnauthorizedException("Invalid authentication token")

    user = await user_service.get_user_by_id(user_id)

    if not user:
        raise UnauthorizedException("User not found")

    if not user.is_active:
        raise ForbiddenException("User is inactive")

    return user

async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise ForbiddenException("Admin permissions required")
    return current_user